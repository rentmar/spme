# spme/spme_repositorio/repositories/garage/client.py
"""
Configuración y creación del cliente boto3 para Garage.
"""

"""
Configuración y creación del cliente boto3 para Garage.

Responsabilidad única:
    ¿Cómo me conecto a Garage?

El resto de la aplicación no crea clientes boto3 directamente.
"""

import boto3
from botocore.config import Config
from django.conf import settings


def crear_cliente_garage():
    """
    Crea y retorna un cliente boto3 configurado para Garage.

    Encapsula:
        - endpoint_url
        - credenciales
        - región
        - configuración del cliente S3
    """
    garage_config = settings.GARAGE_CONFIG

    config = Config(
        signature_version='s3v4',
        s3={'addressing_style': 'path'},
    )

    return boto3.client(
        's3',
        endpoint_url=garage_config['endpoint_url'],
        aws_access_key_id=garage_config['aws_access_key_id'],
        aws_secret_access_key=garage_config['aws_secret_access_key'],
        region_name=garage_config['region_name'],
        use_ssl=garage_config.get('use_ssl', False),
        verify=garage_config.get('verify', False),
        config=config,
    )

# import boto3
# from botocore.config import Config
# from django.conf import settings


# def crear_cliente_garage():
#     """Crea y retorna un cliente boto3 configurado para Garage."""
#     config = Config(
#         signature_version='s3v4',
#         s3={'addressing_style': 'path'}
#     )

#     return boto3.client(
#         's3',
#         endpoint_url=settings.GARAGE_CONFIG['endpoint_url'],
#         aws_access_key_id=settings.GARAGE_CONFIG['aws_access_key_id'],
#         aws_secret_access_key=settings.GARAGE_CONFIG['aws_secret_access_key'],
#         region_name=settings.GARAGE_CONFIG['region_name'],
#         use_ssl=settings.GARAGE_CONFIG['use_ssl'],
#         verify=settings.GARAGE_CONFIG['verify'],
#         config=config,
#    )
