"""
Servicio de aplicación para almacenamiento en Garage.

Ofrece una interfaz cómoda para Django,
ocultando los detalles de S3/boto3.

Dependencia:
    GarageService → ObjectRepository → boto3 → Garage

El bucket debe existir previamente como parte de la
infraestructura de Garage. No se crea automáticamente.
"""

import uuid
import hashlib
import re
import logging
from unicodedata import normalize
from typing import Dict

from django.core.files.uploadedfile import UploadedFile
from django.conf import settings

from spme_repositorio.repositories.garage.object_repository import ObjectRepository
from spme_repositorio.nodos_config import get_carpeta

logger = logging.getLogger(__name__)


class GarageService:
    """
    Servicio de alto nivel para operaciones de archivos en Garage.

    No sabe nada de boto3. Solo delega en ObjectRepository.
    """

    def __init__(self):
        self._repo = ObjectRepository()
        self._bucket = settings.GARAGE_BUCKET

    def _sanitizar_nombre(self, nombre: str) -> str:
        """Limpia el nombre del archivo para storage."""
        partes = nombre.rsplit('.', 1)
        nombre_base = partes[0]
        extension = partes[1] if len(partes) > 1 else ''

        nombre_base = normalize('NFKD', nombre_base).encode('ASCII', 'ignore').decode('ASCII')
        nombre_base = re.sub(r'[^\w\s-]', '', nombre_base)
        nombre_base = re.sub(r'[-\s]+', '_', nombre_base).strip('-_')

        if extension:
            return f"{nombre_base}.{extension}"
        return nombre_base

    def _calcular_sha256(self, file_obj: UploadedFile) -> str:
        """Calcula el hash SHA256 del archivo."""
        sha256 = hashlib.sha256()
        file_obj.seek(0)
        for chunk in file_obj.chunks():
            sha256.update(chunk)
        file_obj.seek(0)
        return sha256.hexdigest()

    def _generar_key(self, tipo_objeto: str, objeto_id: int, nombre_original: str) -> str:
        """
        Genera la key estructurada en Garage.

        Formato: {carpeta}/{objeto_id}/{uuid}/{nombre}
        Ejemplo: actividades/42/a1b2c3d4/informe_final.pdf
        """
        carpeta = get_carpeta(tipo_objeto)

        file_uuid = uuid.uuid4()
        nombre_sanitizado = self._sanitizar_nombre(nombre_original)
        return f"{carpeta}/{objeto_id}/{file_uuid}/{nombre_sanitizado}"

    def subir(self, file_obj: UploadedFile, tipo_objeto: str, objeto_id: int) -> Dict:
        """
        Sube un archivo a Garage.

        Returns:
            Dict con metadatos listos para crear un registro Archivo
        """
        key = self._generar_key(tipo_objeto, objeto_id, file_obj.name)
        file_hash = self._calcular_sha256(file_obj)

        self._repo.put(
            bucket=self._bucket,
            key=key,
            body=file_obj,
            content_type=file_obj.content_type or 'application/octet-stream',
        )

        logger.info(f"Archivo subido a Garage: {key}")

        return {
            'nombre_original': file_obj.name,
            'nombre_storage': key.split('/')[-1],
            'mime_type': file_obj.content_type or 'application/octet-stream',
            'tamano': file_obj.size,
            'bucket': self._bucket,
            'key': key,
            'hash_sha256': file_hash,
        }

    def obtener_metadata(self, key: str) -> Dict:
        """Obtiene metadatos sin descargar. Retorna None si no existe."""
        return self._repo.head(self._bucket, key)

    def descargar(self, key: str) -> Dict:
        """Obtiene un archivo. Retorna un stream."""
        return self._repo.get(self._bucket, key)

    def eliminar(self, key: str) -> None:
        """
        Elimina un archivo de Garage.
        DeleteObject es idempotente. Si hay error real, se propaga.
        """
        self._repo.delete(self._bucket, key)

    def generar_url_descarga(self, archivo, expiration: int = 900):
        """
        Genera una URL prefirmada para descargar un archivo.
        
        Args:
            archivo: Instancia Archivo (debe tener bucket, key, nombre_original)
            expiration: Tiempo de expiración en segundos (default 15 min)
        
        Returns:
            URL prefirmada para descarga directa desde Garage
        """
        response_disposition = f'attachment; filename="{archivo.nombre_original}"'
        
        return self._repo.generate_presigned_url(
            archivo.bucket,
            archivo.key,
            expiration=expiration,
            response_content_disposition=response_disposition,
        )

    # def generar_url_descarga(self, archivo, expiration: int = 900):
    #     """
    #     Genera una URL prefirmada para descargar un archivo.
    #     Args:
    #         archivo: Instancia Archivo (debe tener bucket y key)
    #         expiration: Tiempo de expiración en segundos (default 15 min)
        
    #     Returns:
    #         URL prefirmada para descarga directa desde Garage
    #     """
    #     return self._repo.generate_presigned_url(
    #         archivo.bucket,
    #         archivo.key,
    #         expiration=expiration,
    #     )