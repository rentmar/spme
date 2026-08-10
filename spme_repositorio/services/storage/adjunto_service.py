# spme/spme_repositorio/services/storage/adjunto_service.py
"""
Servicio de aplicación para la gestión de Adjuntos.

Coordina:
    ArchivoService (creación/eliminación de Archivos)
        +
    Adjunto (asociación vía ContentType)

API:
    subir_y_asociar()              → 1 archivo → Adjunto
    subir_multiples_y_asociar()    → N archivos → ResultadoSubidaMultiple
    asociar()                      → Archivo existente → Adjunto
    desasociar()                   → Elimina Adjunto, conserva Archivo
    eliminar_adjunto_y_archivo()   → Elimina Adjunto + Archivo si no tiene más asociaciones
    obtener_adjuntos()             → Lista adjuntos de un objeto
"""

import logging
from dataclasses import dataclass
from typing import List

from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from spme_repositorio.models import Archivo, Adjunto
from spme_repositorio.services.storage.archivo_service import ArchivoService
from spme_repositorio.repositories.garage.exceptions import GarageError
from .exceptions import AdjuntoCreationError

logger = logging.getLogger(__name__)

CLASE_TO_TIPO = {
    'indicadorobjetivogeneral': 'indicador_og',
    'indicadorresultadoobjgral': 'indicador_rog',
    'indicadorobjetivoespecifico': 'indicador_oe',
    'indicadorresultadoobjespecifico': 'indicador_roe',
    'actividad': 'actividad',
    'tareaactividad': 'tarea',
}


@dataclass
class ResultadoSubida:
    nombre_original: str
    error: str


@dataclass
class ResultadoSubidaMultiple:
    exitosos: List[Adjunto]
    fallidos: List[ResultadoSubida]

    @property
    def total(self) -> int:
        return len(self.exitosos) + len(self.fallidos)

    @property
    def todos_exitosos(self) -> bool:
        return not self.fallidos


class AdjuntoService:

    def __init__(self):
        self._archivo_service = ArchivoService()

    def _get_tipo_objeto(self, content_object) -> str:
        clase_nombre = content_object.__class__.__name__.lower()
        return CLASE_TO_TIPO.get(clase_nombre, 'otros')

    @transaction.atomic
    def subir_y_asociar(
        self,
        file_obj: UploadedFile,
        tipo_objeto: str,
        content_object,
        creado_por,
        descripcion: str = '',
        orden: int = 0,
    ) -> Adjunto:
        """
        Sube un archivo a Garage, crea el Archivo en MySQL
        y lo asocia al objeto de negocio.

        Si falla la creación del Adjunto, intenta compensar eliminando
        el Archivo. Si la compensación falla, registra el error crítico.
        """
        tipo_objeto = self._get_tipo_objeto(content_object)

        # 1. Subir archivo (Garage + MySQL)
        archivo = self._archivo_service.subir(
            file_obj=file_obj,
            tipo_objeto=tipo_objeto,
            objeto_id=content_object.pk,
            creado_por=creado_por,
        )

        # 2. Crear Adjunto
        try:
            adjunto = Adjunto.objects.create(
                archivo=archivo,
                content_object=content_object,
                descripcion=descripcion,
                orden=orden,
                creado_por=creado_por,
            )
        except Exception as e:
            # Compensación: eliminar Archivo (Garage + MySQL)
            self._archivo_service._compensar_garage(archivo.key, e)
            try:
                archivo.delete()
            except Exception:
                logger.error(f"No se pudo eliminar Archivo {archivo.id} durante compensación")
            logger.error(
                f"Compensación: Archivo {archivo.id} eliminado "
                f"por fallo al crear Adjunto"
            )
            raise AdjuntoCreationError("No se pudo crear el adjunto") from e

        logger.info(
            f"Adjunto creado: {adjunto.id} - "
            f"{archivo.nombre_original} → "
            f"{content_object._meta.model_name}#{content_object.pk}"
        )
        return adjunto

    def subir_multiples_y_asociar(
        self,
        files: list,
        tipo_objeto: str,
        content_object,
        creado_por,
        descripcion: str = '',
    ) -> ResultadoSubidaMultiple:
        """
        Sube múltiples archivos y los asocia al objeto.

        Cada archivo es independiente con su propia transacción.
        Si uno falla, los demás permanecen guardados.
        """
        exitosos = []
        fallidos = []

        for i, file_obj in enumerate(files):
            try:
                adjunto = self.subir_y_asociar(
                    file_obj=file_obj,
                    tipo_objeto=tipo_objeto,
                    content_object=content_object,
                    creado_por=creado_por,
                    descripcion=descripcion,
                    orden=i,
                )
                exitosos.append(adjunto)
            except Exception as e:
                fallidos.append(ResultadoSubida(
                    nombre_original=file_obj.name,
                    error=str(e),
                ))
                logger.error(f"Error al subir {file_obj.name}: {e}")

        logger.info(
            f"Subida múltiple: {len(exitosos)} exitoso(s), "
            f"{len(fallidos)} fallido(s) → "
            f"{content_object._meta.model_name}#{content_object.pk}"
        )
        return ResultadoSubidaMultiple(exitosos=exitosos, fallidos=fallidos)

    def asociar(
        self,
        archivo: Archivo,
        content_object,
        creado_por,
        descripcion: str = '',
        orden: int = 0,
    ) -> Adjunto:
        """Asocia un Archivo existente a un objeto de negocio."""
        adjunto = Adjunto.objects.create(
            archivo=archivo,
            content_object=content_object,
            descripcion=descripcion,
            orden=orden,
            creado_por=creado_por,
        )
        logger.info(
            f"Archivo {archivo.id} asociado a "
            f"{content_object._meta.model_name}#{content_object.pk}"
        )
        return adjunto

    def desasociar(self, adjunto: Adjunto) -> None:
        """Elimina solo la asociación. No elimina el Archivo ni Garage."""
        archivo_id = adjunto.archivo_id
        adjunto.delete()
        logger.info(f"Adjunto eliminado. Archivo {archivo_id} conservado.")

    def eliminar_adjunto_y_archivo(self, adjunto: Adjunto) -> None:
        """
        Elimina el Adjunto y, si el Archivo no tiene más asociaciones,
        elimina también el Archivo y el objeto en Garage.
        """
        archivo = adjunto.archivo
        adjunto.delete()

        if not archivo.adjuntos.exists():
            self._archivo_service.eliminar(archivo)
        else:
            logger.info(
                f"Archivo {archivo.id} conservado: "
                f"aún tiene {archivo.adjuntos.count()} adjunto(s)."
            )

    def obtener_adjuntos(self, content_object) -> list:
        """Obtiene todos los adjuntos de un objeto, ordenados."""
        ct = ContentType.objects.get_for_model(content_object)
        return list(
            Adjunto.objects.filter(
                content_type=ct,
                object_id=content_object.pk,
            )
            .select_related('archivo')
            .order_by('orden', '-creado_en')
        )