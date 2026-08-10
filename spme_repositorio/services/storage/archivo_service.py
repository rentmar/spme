# spme/spme_repositorio/services/storage/archivo_service.py
"""
Servicio de aplicación para la gestión de Archivos.

Coordina:
    GarageService (almacenamiento físico)
        +
    Archivo (registro en MySQL)

Determina el tipo_archivo desde el MIME type.
Maneja compensación si MySQL falla después de subir a Garage.
"""

import logging

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction, IntegrityError

from spme_repositorio.models import Archivo
from spme_repositorio.services.storage.garage_service import GarageService
from spme_repositorio.repositories.garage.exceptions import GarageError
from .exceptions import ArchivoCreationError, ArchivoStillReferencedError

logger = logging.getLogger(__name__)


class ArchivoService:
    """
    Servicio para crear y gestionar registros Archivo.

    Responsabilidades:
        - Subir archivo a Garage (delega en GarageService)
        - Determinar tipo_archivo desde MIME type (por familia)
        - Crear registro Archivo en MySQL
        - Compensar si MySQL falla (eliminar de Garage)
        - Eliminar archivo solo si no tiene adjuntos asociados
    """

    def __init__(self):
        self._garage = GarageService()

    def _determinar_tipo(self, mime_type: str, nombre_original: str = '') -> str:
        """
        Determina el tipo lógico del archivo.

        Prioridad:
            1. MIME type
            2. Extensión del archivo
            3. OTRO
        """
        mime_type = (mime_type or '').lower()

        # MIME
        if mime_type.startswith('image/'):
            return 'IMAGEN'
        if mime_type.startswith('video/'):
            return 'VIDEO'
        if mime_type.startswith('audio/'):
            return 'AUDIO'
        if mime_type in (
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'text/plain',
            'text/csv',
        ):
            return 'DOCUMENTO'

        # Fallback por extensión
        extension = nombre_original.rsplit('.', 1)[-1].lower() if '.' in nombre_original else ''

        if extension in {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'xlsm', 'ppt', 'pptx', 'txt', 'csv', 'odt', 'ods', 'odp'}:
            return 'DOCUMENTO'
        if extension in {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg'}:
            return 'IMAGEN'
        if extension in {'mp4', 'webm', 'avi', 'mov', 'mkv'}:
            return 'VIDEO'
        if extension in {'mp3', 'wav', 'ogg', 'm4a', 'flac'}:
            return 'AUDIO'

        return 'OTRO'

    def _compensar_garage(self, key: str, error_original: Exception) -> None:
        """
        Intenta compensar eliminando de Garage.
        Si la compensación falla, registra el error crítico pero no
        oculta el error original.
        """
        try:
            self._garage.eliminar(key)
        except GarageError as cleanup_error:
            logger.critical(
                "No se pudo compensar archivo en Garage",
                extra={
                    "key": key,
                    "error_original": str(error_original),
                    "error_compensacion": str(cleanup_error),
                },
            )

    @transaction.atomic
    def subir(
        self,
        file_obj: UploadedFile,
        tipo_objeto: str,
        objeto_id: int,
        creado_por,
    ) -> Archivo:
        """
        Sube un archivo a Garage y crea el registro en MySQL.

        Si MySQL falla, intenta eliminar el archivo de Garage como compensación.
        Si la compensación también falla, registra el error crítico.

        Args:
            file_obj: Archivo de request.FILES
            tipo_objeto: 'indicador', 'actividad', 'tarea', etc.
            objeto_id: ID del objeto al que pertenece
            creado_por: Usuario que sube el archivo

        Returns:
            Instancia Archivo creada

        Raises:
            ArchivoCreationError: Si falla la creación en MySQL
        """
        # 1. Subir a Garage (errores de Garage se propagan solos)
        metadata = self._garage.subir(file_obj, tipo_objeto, objeto_id)

        # 2. Determinar tipo
        tipo_archivo = self._determinar_tipo(metadata['mime_type'], metadata['nombre_original'])

        # 3. Crear registro en MySQL
        try:
            archivo = Archivo.objects.create(
                nombre_original=metadata['nombre_original'],
                nombre_storage=metadata['nombre_storage'],
                tipo_archivo=tipo_archivo,
                mime_type=metadata['mime_type'],
                tamano=metadata['tamano'],
                bucket=metadata['bucket'],
                key=metadata['key'],
                hash_sha256=metadata['hash_sha256'],
                creado_por=creado_por,
            )
        except IntegrityError as e:
            # Compensación: eliminar de Garage
            self._compensar_garage(metadata['key'], e)
            raise ArchivoCreationError("Error de integridad al registrar archivo") from e
        except Exception as e:
            # Compensación: eliminar de Garage
            self._compensar_garage(metadata['key'], e)
            raise ArchivoCreationError("No se pudo registrar el archivo") from e

        logger.info(f"Archivo creado: {archivo.id} - {archivo.nombre_original}")
        return archivo

    def eliminar(self, archivo: Archivo) -> None:
        """
        Elimina un archivo de Garage y su registro en MySQL.

        Solo elimina si no tiene adjuntos asociados.
        Si aún tiene adjuntos, lanza ArchivoStillReferencedError.
        Si Garage falla, el error se propaga y MySQL no se toca.
        """
        if archivo.adjuntos.exists():
            raise ArchivoStillReferencedError(
                f"No se puede eliminar el archivo {archivo.id}: "
                f"aún tiene {archivo.adjuntos.count()} adjunto(s) asociado(s)."
            )

        # 1. Eliminar de Garage (si falla, se propaga y no tocamos MySQL)
        self._garage.eliminar(archivo.key)

        # 2. Eliminar de MySQL
        archivo.delete()

        logger.info(f"Archivo eliminado: {archivo.id} - {archivo.nombre_original}")