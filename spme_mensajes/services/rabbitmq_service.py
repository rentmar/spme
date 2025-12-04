import json
import logging
import pika
import time
from typing import Dict, List, Optional, Any, Callable
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

class RabbitMQService:
    """
    Servicio completo para interactuar con RabbitMQ
    
    Configuración basada en tu RabbitMQ:
    COLA                  BINDING CONFIGURADO
    --------------------------------------------------
    correo                ✓ notificaciones_exchange → notificacion.correo.#
    mensajes_usuarios     ✓ notificaciones_exchange → mensaje.usuario.#  
    mensajes_grupales     ✓ notificaciones_exchange → mensaje.grupo.#
    sistema_alertas       ✓ notificaciones_exchange → sistema.#
    cola_reintentos       ✓ dlx_notificaciones → (vacío)
    cola_alertas_fallidas ✓ dlx_critico → (vacío)
    """

    #Configuracion de conexion
    # Configuración de conexión (ajustar según tu entorno)
    _host = getattr(settings, 'RABBITMQ_HOST', 'localhost')
    _port = getattr(settings, 'RABBITMQ_PORT', 5672)
    _username = getattr(settings, 'RABBITMQ_USERNAME', 'admin')
    _password = getattr(settings, 'RABBITMQ_PASSWORD', 'admin')
    _virtual_host = getattr(settings, 'RABBITMQ_VIRTUAL_HOST', '/')

    