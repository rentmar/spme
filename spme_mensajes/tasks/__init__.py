# Importar tareas para que estén disponibles
from .correos_especificos import *
from .mensaje_tasks import *
from .tareas_prueba import *

__all__ = [
    # Tareas de correo
    'enviar_correo_prueba_sistema',
    'enviar_correo_solicitud_pendiente',
    'enviar_correo_solicitud_aprobada',
    'enviar_correo_solicitud_rechazada',

    #Tareas periodicas
    'enviar_correo_prueba_beat', 
    'tarea_beat_prueba',
    
    # Tareas de mensajes
    'enviar_mensaje_usuario',
    'enviar_notificacion_sistema',
    'enviar_alerta_actividad',
]