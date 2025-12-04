# Importar tareas para que estén disponibles
from .correos_especificos import *
from .mensaje_tasks import *

__all__ = [
    # Tareas de correo
    'enviar_correo_prueba_sistema',
    'enviar_correo_solicitud_pendiente',
    'enviar_correo_solicitud_aprobada',
    
    # Tareas de mensajes
    'enviar_mensaje_usuario',
    'enviar_notificacion_sistema',
    'enviar_alerta_actividad',
]