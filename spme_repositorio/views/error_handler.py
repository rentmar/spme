"""
Handler global de excepciones para el repositorio.
Convierte excepciones propias en respuestas HTTP.
"""

from rest_framework import status
from rest_framework.response import Response

from spme_repositorio.repositories.garage.exceptions import (
    GarageConnectionError,
    GarageObjectNotFoundError,
    GarageBucketNotFoundError,
    GarageUploadError,
    GarageDownloadError,
    GarageDeleteError,
)
from spme_repositorio.services.storage.exceptions import (
    ArchivoCreationError,
    AdjuntoCreationError,
    ArchivoIntegrityError,
    AdjuntoNotFoundError,
    ArchivoNotFoundError,
    ArchivoStillReferencedError,
)

ERROR_MAP = {
    GarageConnectionError: (status.HTTP_502_BAD_GATEWAY, 'Error de conexión con el almacenamiento'),
    GarageObjectNotFoundError: (status.HTTP_404_NOT_FOUND, 'Archivo no encontrado en almacenamiento'),
    GarageBucketNotFoundError: (status.HTTP_500_INTERNAL_SERVER_ERROR, 'Configuración de almacenamiento incorrecta'),
    GarageUploadError: (status.HTTP_502_BAD_GATEWAY, 'Error al guardar archivo en almacenamiento'),
    GarageDownloadError: (status.HTTP_502_BAD_GATEWAY, 'Error al descargar archivo desde almacenamiento'),
    GarageDeleteError: (status.HTTP_502_BAD_GATEWAY, 'Error al eliminar archivo de almacenamiento'),
    ArchivoCreationError: (status.HTTP_500_INTERNAL_SERVER_ERROR, 'Error al registrar archivo'),
    AdjuntoCreationError: (status.HTTP_500_INTERNAL_SERVER_ERROR, 'Error al registrar adjunto'),
    ArchivoIntegrityError: (status.HTTP_409_CONFLICT, 'Conflicto de integridad'),
    AdjuntoNotFoundError: (status.HTTP_404_NOT_FOUND, 'Adjunto no encontrado'),
    ArchivoNotFoundError: (status.HTTP_404_NOT_FOUND, 'Archivo no encontrado'),
    ArchivoStillReferencedError: (status.HTTP_409_CONFLICT, 'El archivo aún tiene referencias'),
}


def repositorio_exception_handler(exc, context):
    """
    Handler global de excepciones para el repositorio.
    
    Convierte excepciones propias en respuestas HTTP.
    Si la excepción no está mapeada, retorna None para que
    DRF use su handler por defecto.
    """
    for exc_class, (http_status, message) in ERROR_MAP.items():
        if isinstance(exc, exc_class):
            return Response(
                {'error': message, 'detalle': str(exc)},
                status=http_status,
            )
    return None