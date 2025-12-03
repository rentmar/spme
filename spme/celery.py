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
)

#Ruteo de tareas
app.conf.task_routes = {
    # Todas las tareas de correo van a la cola 'correo'
    'spme_mensajes.tasks.*': {
        'queue': 'correo',
        'routing_key': 'notificacion.correo'
    },
}

# CONFIGURACIÓN GLOBAL DE CELERY
app.conf.broker_connection_retry_on_startup = True
app.conf.worker_prefetch_multiplier = 1
app.conf.task_acks_late = True
app.conf.task_reject_on_worker_lost = True
app.conf.task_default_priority = 5
app.conf.task_queue_max_priority = 10

# Retry configuration
app.conf.task_annotations = {
    'spme_mensajes.tasks.enviar_correo_verificacion': {
        'max_retries': 3,
        'default_retry_delay': 60,
    },
    'spme_mensajes.tasks.enviar_correo_notificacion': {
        'max_retries': 2,
        'default_retry_delay': 30,
    },
}

#Autodescubrir tareas
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"[DEBUG] Tarea ejecutada en cola: {self.request.delivery_info.get('routing_key', 'desconocida')}")
    return {'status': 'ok', 'queue': 'correo'}

