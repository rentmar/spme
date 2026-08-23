# spme/spme_repositorio/repositories/garage/object_repository.py
"""
Adaptador de infraestructura para S3/Garage.

Traduce operaciones de aplicación → boto3 → Garage.
No contiene lógica de negocio.
"""

import logging
from typing import BinaryIO, Optional, Dict

from botocore.exceptions import ClientError
from .client import crear_cliente_garage
from .exceptions import (
    GarageConnectionError,
    GarageObjectNotFoundError,
    GarageBucketNotFoundError,
    GarageUploadError,
    GarageDownloadError,
    GarageDeleteError,
)

logger = logging.getLogger(__name__)


class ObjectRepository:
    """Repositorio de objetos en Garage. Operaciones CRUD puras sobre S3."""

    def __init__(self):
        self._client = crear_cliente_garage()

    def put(
        self,
        bucket: str,
        key: str,
        body: BinaryIO,
        content_type: str = 'application/octet-stream',
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict:
        """Guarda un objeto en Garage."""
        extra_args = {'ContentType': content_type}
        if metadata:
            extra_args['Metadata'] = metadata

        try:
            self._client.put_object(Bucket=bucket, Key=key, Body=body, **extra_args)
        except ClientError as e:
            code = e.response['Error']['Code']
            if code == 'NoSuchBucket':
                raise GarageBucketNotFoundError(f"Bucket '{bucket}' no existe") from e
            raise GarageUploadError(f"Error al subir objeto: {e}") from e
        except Exception as e:
            raise GarageConnectionError(f"Sin conexión a Garage: {e}") from e

        logger.info(f"Objeto guardado: {bucket}/{key}")
        return {'bucket': bucket, 'key': key, 'content_type': content_type}

    def head(self, bucket: str, key: str) -> Optional[Dict]:
        """Obtiene metadatos sin descargar."""
        try:
            response = self._client.head_object(Bucket=bucket, Key=key)
            return {
                'content_type': response.get('ContentType'),
                'content_length': response.get('ContentLength'),
                'last_modified': response.get('LastModified'),
                'metadata': response.get('Metadata', {}),
            }
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return None
            raise GarageConnectionError(f"Error al obtener metadata: {e}") from e
        except Exception as e:
            raise GarageConnectionError(f"Sin conexión a Garage: {e}") from e

    def get(self, bucket: str, key: str) -> Dict:
        """Obtiene un objeto de Garage."""
        try:
            response = self._client.get_object(Bucket=bucket, Key=key)
        except ClientError as e:
            code = e.response['Error']['Code']
            if code == 'NoSuchKey':
                raise GarageObjectNotFoundError(f"Objeto '{key}' no encontrado") from e
            raise GarageDownloadError(f"Error al descargar: {e}") from e
        except Exception as e:
            raise GarageConnectionError(f"Sin conexión a Garage: {e}") from e

        return {
            'body': response['Body'],
            'content_type': response.get('ContentType'),
            'content_length': response.get('ContentLength'),
        }

    def delete(self, bucket: str, key: str) -> None:
        """Elimina un objeto de Garage."""
        try:
            self._client.delete_object(Bucket=bucket, Key=key)
        except ClientError as e:
            raise GarageDeleteError(f"Error al eliminar: {e}") from e
        except Exception as e:
            raise GarageConnectionError(f"Sin conexión a Garage: {e}") from e

        logger.info(f"Objeto eliminado: {bucket}/{key}")

    def generate_presigned_url(
        self,
        bucket: str,
        key: str,
        expiration: int = 3600,
        response_content_disposition: Optional[str] = None,
    ) -> str:
        """
        Genera URL prefirmada para acceso temporal.
        
        Args:
            bucket: Nombre del bucket
            key: Ruta del archivo en Garage
            expiration: Tiempo de expiración en segundos
            response_content_disposition: Header Content-Disposition
                (ej: 'attachment; filename="archivo.xlsx"')
        
        Returns:
            URL prefirmada firmada
        """
        try:
            params = {'Bucket': bucket, 'Key': key}
            
            if response_content_disposition:
                params['ResponseContentDisposition'] = response_content_disposition
            
            return self._client.generate_presigned_url(
                'get_object',
                Params=params,
                ExpiresIn=expiration,
            )
        except Exception as e:
            raise GarageConnectionError(f"Error al generar URL: {e}") from e

    # def generate_presigned_url(self, bucket: str, key: str, expiration: int = 3600) -> str:
    #     """
    #     Genera URL prefirmada para acceso temporal.
    #     """
    #     try:
    #         return self._client.generate_presigned_url(
    #             'get_object',
    #             Params={'Bucket': bucket, 'Key': key},
    #             ExpiresIn=expiration,
    #         )
    #     except Exception as e:
    #         raise GarageConnectionError(f"Error al generar URL: {e}") from e