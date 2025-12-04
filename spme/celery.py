import os
from celery import Celery
from kombu import Exchange, Queue

#Configurar los settings de django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spme.settings')

app = Celery('spme')

#Configuracion desde settings
app.config_from_object('django.conf:settings', namespace='CELERY')

#Definiciones de exchanges
notificaciones_exchange = Exchange('notificaciones_exchange', type='topic', durable=True)
dlx_notificaciones = Exchange('dlx_notificaciones', type='direct', durable=True)
dlx_critico = Exchange('dlx_critico', type='fanout', durable=True)

#Configurar las colas especificas
app.conf.task_queues = (
    #Cola correo
    Queue(
        'correo',
        exchange=notificaciones_exchange,
        routing_key='notificacion.correo.#',
        queue_arguments = {
            "x-dead-letter-exchange": "dlx_notificaciones",
            "x-max-length": 50000,
            "x-max-priority": 10,
            "x-message-ttl": 86400000, #24Hrs en ms
            "x-queue-mode": "lazy",
        },
    ),
    Queue(
        'mensajes_usuarios',
        exchange=notificaciones_exchange,
        routing_key='mensaje.usuario.#',
        queue_arguments={
            "x-dead-letter-exchange": "dlx_notificaciones",
            "x-max-length": 100000,
            "x-message-ttl": 2592000000,
            "x-overflow": "reject-publish",
        },
    ),
    Queue(
        'sistema_alertas',
        exchange=notificaciones_exchange,
        routing_key='sistema.#',
        queue_arguments={
            "x-dead-letter-exchange": "dlx_critico",
            "x-max-length": 10000,
            "x-max-priority": 10,  # ✅ Alertas SÍ tienen prioridades
            "x-message-ttl": 172800000,
            "x-queue-mode": "lazy",
        },
    ),
    Queue(
        'mensajes_grupales',
        exchange=notificaciones_exchange,
        routing_key='mensaje.grupo.#',
        queue_arguments={
            "x-max-length": 25000,
            "x-message-ttl": 604800000,
            "x-single-active-consumer": True,
        },
    ),
)

#Ruteo de tareas
app.conf.task_routes = {
    # Todas las tareas de correo van a la cola 'correo'
    # 'spme_mensajes.tasks.*': {
    #     'queue': 'correo',
    #     'routing_key': 'notificacion.correo'
    # },
    'spme_mensajes.tasks.correos_especificos.*': {
        'queue': 'correo',
        'routing_key': 'notificacion.correo'
    },
    'correo.*': {
        'queue': 'correo',
        'routing_key': 'notificacion.correo'
    },
    #Mensajes de usuario
    'spme_mensajes.tasks.mensaje_tasks.*': {
        'queue': 'mensajes_usuarios',
        'routing_key': 'mensaje.usuario'
    },
    'mensajes.*': {
        'queue': 'mensajes_usuarios',
        'routing_key': 'mensaje.usuario'
    },
    #Sistema de alertas
    'sistema.*': {
        'queue': 'sistema_alertas',
        'routing_key': 'sistema'
    },
    #Mensajes grupales
    'grupo.*': {
        'queue': 'mensajes_grupales',
        'routing_key': 'mensaje.grupo'
    },
    #Tareas de mantenimiento
    'mensajes.limpiar_mensajes_expirados': {
        'queue': 'mensajes_usuarios',
        'routing_key': 'mensaje.usuario.mantenimiento'
    },
    'mensajes.actualizar_estadisticas': {
        'queue': 'mensajes_usuarios',
        'routing_key': 'mensaje.usuario.mantenimiento'
    },
}

# CONFIGURACIÓN GLOBAL DE CELERY
app.conf.broker_connection_retry_on_startup = True
app.conf.worker_prefetch_multiplier = 1 #Una tarea a la vez por worker
app.conf.task_acks_late = True #ack despues de procesar
app.conf.task_reject_on_worker_lost = True #Rechazar si worker se pierde
#app.conf.task_default_priority = 5  #Prioridad media por defecto
#app.conf.task_queue_max_priority = 10 # Máxima prioridad soportada

# Timeouts
app.conf.task_time_limit = 300  # 5 minutos máximo por tarea
app.conf.task_soft_time_limit = 240  # 4 minutos warning

# Retry configuration
app.conf.task_annotations = {
    #Correos
    # 'spme_mensajes.tasks.enviar_correo_verificacion': {
    #     'max_retries': 3,
    #     'default_retry_delay': 60,
    # },
    # 'spme_mensajes.tasks.enviar_correo_notificacion': {
    #     'max_retries': 2,
    #     'default_retry_delay': 30,
    # },
    'spme_mensajes.tasks.correos_especificos.enviar_correo_prueba_sistema': {
        'max_retries': 2,
        'default_retry_delay': 30,
    },
    'spme_mensajes.tasks.correos_especificos.enviar_correo_solicitud_pendiente': {
        'max_retries': 3,
        'default_retry_delay': 60,
    },
    'spme_mensajes.tasks.correos_especificos.enviar_correo_solicitud_aprobada': {
        'max_retries': 3,
        'default_retry_delay': 60,
    },
    #Mensajeria de usuarios
    'spme_mensajes.tasks.mensaje_tasks.consumir_mensajes_usuarios': {
        'max_retries': 5,
        'default_retry_delay': 30,
        'retry_backoff': True,
        'retry_backoff_max': 300,  # 5 minutos máximo
    },
    'spme_mensajes.tasks.mensaje_tasks.procesar_mensaje_usuario': {
        'max_retries': 3,
        'default_retry_delay': 30,
    },
    #Tareas de mantenimiento
    'spme_mensajes.tasks.mensaje_tasks.limpiar_mensajes_expirados': {
        'max_retries': 1,
        'default_retry_delay': 60,
    },
}

#Configuracion de tareas periodicas (celery beat)
app.conf.beat_schedule ={
    # Limpiar mensajes expirados cada día a las 2 AM
    'limpiar-mensajes-expirados': {
        'task': 'mensajes.limpiar_mensajes_expirados',
        'schedule': 86400.0,  # 24 horas en segundos
        'options': {
            'queue': 'mensajes_usuarios',
            'routing_key': 'mensaje.usuario.mantenimiento',
        },
    },
    # Actualizar estadísticas cada hora
    'actualizar-estadisticas-mensajes': {
        'task': 'mensajes.actualizar_estadisticas',
        'schedule': 3600.0,  # 1 hora en segundos
        'options': {
            'queue': 'mensajes_usuarios',
            'routing_key': 'mensaje.usuario.mantenimiento',
        },
    },
    # Verificar consumidor de mensajes cada 5 minutos
    'verificar-consumidor-mensajes': {
        'task': 'mensajes.consumir_cola_usuarios',
        'schedule': 300.0,  # 5 minutos en segundos
        'options': {
            'queue': 'mensajes_usuarios',
            'routing_key': 'mensaje.usuario.*',
        },
    },
}

# Definir exchanges en Celery (para que Celery los declare)
app.conf.broker_transport_options = {
    'confirm_publish': True,
    'visibility_timeout': 1800,  # 30 minutos
}



#Autodescubrir tareas
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"[DEBUG] Tarea ejecutada en cola: {self.request.delivery_info.get('routing_key', 'desconocida')}")
    return {'status': 'ok', 'queue': 'correo'}

