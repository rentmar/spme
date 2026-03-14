#Tareas Celery para procesamiento de mensajes de usuarios
from celery import shared_task
import logging
import json
from django.utils import timezone
from django.db import transaction
from ..models import MensajeUsuario, TipoMensaje, EstadoMensaje
from ..repositories.mensaje_repository import MensajeRepository
import pika
from django.conf import settings

logger = logging.getLogger(__name__)

# ============================================================================
# CONSUMIDOR RABBITMQ - MENSAJES_USUARIOS
# ============================================================================

@shared_task(
    bind=True,
    name='mensajes.consumir_cola_usuarios',
    queue='mensajes_usuarios',
    #priority=5,
    routing_key='mensaje.usuario.*'
)
def consumir_mensajes_usuarios(self):
    """
    Tarea para consumir mensajes de la cola 'mensajes_usuarios'
    """
    task_id = self.request.id
    
    try:
        logger.info(f"[{task_id}] Iniciando consumidor de mensajes de usuarios")
        
        # Configuración de RabbitMQ
        rabbitmq_config = getattr(settings, 'RABBITMQ_CONFIG', {
            'host': 'localhost',
            'port': 5672,
            'username': 'admin',
            'password': 'admin',
            'vhost': '/'
        })
        
        # Parámetros de conexión
        credentials = pika.PlainCredentials(
            rabbitmq_config['username'],
            rabbitmq_config['password']
        )
        
        parameters = pika.ConnectionParameters(
            host=rabbitmq_config['host'],
            port=rabbitmq_config['port'],
            virtual_host=rabbitmq_config['vhost'],
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        
        # Conectar y consumir
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        # Configurar QoS
        channel.basic_qos(prefetch_count=10)
        
        def callback(ch, method, properties, body):
            """Callback para procesar cada mensaje"""
            try:
                # Decodificar mensaje
                mensaje_data = json.loads(body.decode('utf-8'))
                routing_key = method.routing_key
                
                logger.info(f"[{task_id}] Procesando mensaje: {routing_key}")
                
                # Procesar según el tipo de mensaje
                if routing_key == 'mensaje.usuario.privado':
                    procesar_mensaje_privado(mensaje_data, properties.headers)
                elif routing_key == 'mensaje.usuario.sistema':
                    procesar_mensaje_sistema(mensaje_data, properties.headers)
                elif routing_key == 'mensaje.usuario.alertas':
                    procesar_mensaje_alerta(mensaje_data, properties.headers)
                elif routing_key == 'mensaje.usuario.actividad':
                    procesar_mensaje_actividad(mensaje_data, properties.headers)
                else:
                    logger.warning(f"[{task_id}] Routing key no reconocido: {routing_key}")
                
                # Ack del mensaje
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
                logger.debug(f"[{task_id}] Mensaje procesado y ack enviado")
                
            except json.JSONDecodeError as e:
                logger.error(f"[{task_id}] Error decodificando JSON: {str(e)}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            except Exception as e:
                logger.error(f"[{task_id}] Error procesando mensaje: {str(e)}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        # Configurar consumo
        channel.basic_consume(
            queue='mensajes_usuarios',
            on_message_callback=callback,
            auto_ack=False
        )
        
        logger.info(f"[{task_id}] Consumidor listo. Esperando mensajes...")
        
        # Iniciar consumo
        channel.start_consuming()
        
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"[{task_id}] Error de conexión RabbitMQ: {str(e)}")
        raise self.retry(exc=e, countdown=60)
    except Exception as e:
        logger.error(f"[{task_id}] Error en consumidor: {str(e)}")
        raise

# ============================================================================
# FUNCIONES DE PROCESAMIENTO
# ============================================================================

def procesar_mensaje_privado(mensaje_data, headers):
    """Procesa mensaje privado entre usuarios"""
    try:
        with transaction.atomic():
            mensaje_data_mapped = {
                'remitente_id': mensaje_data.get('remitente_id'),
                'destinatario_id': mensaje_data['destinatario_id'],
                'asunto': mensaje_data['asunto'],
                'contenido': mensaje_data['contenido'],
                'tipo': TipoMensaje.PRIVADO,
                'prioridad': mensaje_data.get('prioridad', 1),
                'routing_key': 'mensaje.usuario.privado',
                'metadata': mensaje_data.get('metadata', {}),
                'referencia_id': mensaje_data.get('referencia_id', ''),
                'fecha_expiracion': mensaje_data.get('fecha_expiracion'),
                'accion_url': mensaje_data.get('accion_url', ''),
                'accion_texto': mensaje_data.get('accion_texto', ''),
                'icono': mensaje_data.get('icono', '✉️'),
            }
            
            mensaje = MensajeRepository.crear_mensaje(mensaje_data_mapped)
            
            logger.info(f"Mensaje privado creado: {mensaje.pk}")
            
            return {
                'success': True,
                'mensaje_id': mensaje.pk,
                'message_id': mensaje.message_id,
                'tipo': TipoMensaje.PRIVADO,
                'timestamp': timezone.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error procesando mensaje privado: {str(e)}")
        raise

def procesar_mensaje_sistema(mensaje_data, headers):
    """Procesa mensaje del sistema"""
    try:
        with transaction.atomic():
            mensaje_data_mapped = {
                'destinatario_id': mensaje_data['destinatario_id'],
                'remitente_id': None,
                'asunto': mensaje_data.get('asunto', 'Notificación del Sistema'),
                'contenido': mensaje_data['contenido'],
                'tipo': TipoMensaje.SISTEMA,
                'prioridad': mensaje_data.get('prioridad', 1),
                'routing_key': 'mensaje.usuario.sistema',
                'metadata': mensaje_data.get('metadata', {}),
                'referencia_id': mensaje_data.get('referencia_id', ''),
                'fecha_expiracion': mensaje_data.get('fecha_expiracion'),
                'accion_url': mensaje_data.get('accion_url', ''),
                'accion_texto': mensaje_data.get('accion_texto', ''),
                'icono': mensaje_data.get('icono', '🔔'),
            }
            
            mensaje = MensajeRepository.crear_mensaje(mensaje_data_mapped)
            
            logger.info(f"Mensaje del sistema creado: {mensaje.pk}")
            
            return {
                'success': True,
                'mensaje_id': mensaje.pk,
                'message_id': mensaje.message_id,
                'tipo': TipoMensaje.SISTEMA,
                'timestamp': timezone.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error procesando mensaje del sistema: {str(e)}")
        raise

def procesar_mensaje_alerta(mensaje_data, headers):
    """Procesa mensaje de alerta"""
    try:
        with transaction.atomic():
            # Mapear tipo de alerta a prioridad
            tipo_alerta = mensaje_data.get('tipo_alerta', 'info')
            prioridad_map = {
                'critica': 3,
                'alta': 3,
                'media': 2,
                'baja': 1,
                'info': 1
            }
            
            prioridad = prioridad_map.get(tipo_alerta, 1)
            
            mensaje_data_mapped = {
                'destinatario_id': mensaje_data['destinatario_id'],
                'remitente_id': None,
                'asunto': mensaje_data.get('asunto', 'Alerta del Sistema'),
                'contenido': mensaje_data['contenido'],
                'tipo': TipoMensaje.ALERTA,
                'prioridad': prioridad,
                'routing_key': 'mensaje.usuario.alertas',
                'metadata': mensaje_data.get('metadata', {}),
                'referencia_id': mensaje_data.get('referencia_id', ''),
                'fecha_expiracion': mensaje_data.get('fecha_expiracion'),
                'accion_url': mensaje_data.get('accion_url', ''),
                'accion_texto': mensaje_data.get('accion_texto', ''),
                'icono': mensaje_data.get('icono', '⚠️'),
            }
            
            mensaje = MensajeRepository.crear_mensaje(mensaje_data_mapped)
            
            logger.info(f"Mensaje de alerta creado: {mensaje.pk}")
            
            return {
                'success': True,
                'mensaje_id': mensaje.pk,
                'message_id': mensaje.message_id,
                'tipo': TipoMensaje.ALERTA,
                'tipo_alerta': tipo_alerta,
                'timestamp': timezone.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error procesando mensaje de alerta: {str(e)}")
        raise

def procesar_mensaje_actividad(mensaje_data, headers):
    """Procesa mensaje relacionado con actividades"""
    try:
        with transaction.atomic():
            # Mapear tipo de evento
            evento_tipo_map = {
                'inicio_inminente': TipoMensaje.RECORDATORIO,
                'retraso': TipoMensaje.RETRASO,
                'reprogramacion': TipoMensaje.REPROGRAMACION,
                'recordatorio': TipoMensaje.RECORDATORIO,
                'completado': TipoMensaje.SISTEMA,
                'actualizacion': TipoMensaje.SISTEMA,
            }
            
            tipo_evento = mensaje_data['tipo_evento']
            tipo_mensaje = evento_tipo_map.get(tipo_evento, TipoMensaje.SISTEMA)
            
            # Mapear prioridad
            evento_prioridad = {
                'inicio_inminente': 2,
                'retraso': 3,
                'reprogramacion': 2,
                'recordatorio': 1,
                'completado': 1,
                'actualizacion': 1,
            }
            
            prioridad = evento_prioridad.get(tipo_evento, 1)
            
            # Generar contenido
            contenido = generar_contenido_actividad(mensaje_data)
            
            mensaje_data_mapped = {
                'destinatario_id': mensaje_data['destinatario_id'],
                'remitente_id': None,
                'asunto': mensaje_data.get('asunto', f"Actividad: {tipo_evento}"),
                'contenido': contenido,
                'tipo': tipo_mensaje,
                'prioridad': prioridad,
                'routing_key': 'mensaje.usuario.actividad',
                'metadata': {
                    'actividad_id': mensaje_data['actividad_id'],
                    'tipo_evento': tipo_evento,
                    'fecha_evento': mensaje_data.get('fecha_evento'),
                    'proyecto_id': mensaje_data.get('proyecto_id'),
                    **mensaje_data.get('metadata', {})
                },
                'referencia_id': f"ACT-{mensaje_data['actividad_id']}",
                'fecha_expiracion': mensaje_data.get('fecha_expiracion'),
                'accion_url': mensaje_data.get('accion_url', ''),
                'accion_texto': mensaje_data.get('accion_texto', 'Ver Actividad'),
                'icono': mensaje_data.get('icono', '📅'),
                'actividad_id': mensaje_data['actividad_id'],
                'proyecto_id': mensaje_data.get('proyecto_id'),
            }
            
            mensaje = MensajeRepository.crear_mensaje(mensaje_data_mapped)
            
            logger.info(f"Mensaje de actividad creado: {mensaje.pk}")
            
            return {
                'success': True,
                'mensaje_id': mensaje.pk,
                'message_id': mensaje.message_id,
                'tipo': tipo_mensaje,
                'tipo_evento': tipo_evento,
                'timestamp': timezone.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error procesando mensaje de actividad: {str(e)}")
        raise

def generar_contenido_actividad(mensaje_data):
    """Genera contenido para mensajes de actividad"""
    tipo_evento = mensaje_data['tipo_evento']
    actividad_nombre = mensaje_data.get('actividad_nombre', 'la actividad')
    fecha_evento = mensaje_data.get('fecha_evento')
    
    contenidos = {
        'inicio_inminente': f"⏰ La actividad '{actividad_nombre}' está por iniciar en 5 días. Prepárate para comenzar.",
        'retraso': f"⚠️ La actividad '{actividad_nombre}' presenta retraso. Revisa los plazos establecidos.",
        'reprogramacion': f"📅 La actividad '{actividad_nombre}' ha sido reprogramada. Verifica las nuevas fechas.",
        'recordatorio': f"🔔 Recordatorio: La actividad '{actividad_nombre}' está próxima a su fecha límite.",
        'completado': f"✅ La actividad '{actividad_nombre}' ha sido completada exitosamente. ¡Buen trabajo!",
        'actualizacion': f"📝 La actividad '{actividad_nombre}' ha sido actualizada. Revisa los cambios realizados.",
    }
    
    contenido = contenidos.get(tipo_evento, f"Notificación sobre la actividad '{actividad_nombre}'")
    
    if fecha_evento:
        contenido += f"\n\nFecha: {fecha_evento}"
    
    return contenido

# ============================================================================
# TAREAS DE MANTENIMIENTO
# ============================================================================

@shared_task(
    name='mensajes.limpiar_mensajes_expirados',
    queue='mensajes_usuarios',
    #priority=3
)
def limpiar_mensajes_expirados():
    """Limpia mensajes expirados"""
    try:
        count = MensajeRepository.limpiar_mensajes_expirados()
        logger.info(f"Mensajes expirados limpiados: {count}")
        return {'limpiados': count}
    except Exception as e:
        logger.error(f"Error limpiando mensajes expirados: {str(e)}")
        return {'error': str(e)}

@shared_task(
    name='mensajes.actualizar_estadisticas',
    queue='mensajes_usuarios',
    #priority=4
)
def actualizar_estadisticas_mensajes():
    """Actualiza estadísticas de mensajes"""
    try:
        # Aquí podrías agregar lógica para generar reportes
        logger.info("Estadísticas de mensajes actualizadas")
        return {'success': True}
    except Exception as e:
        logger.error(f"Error actualizando estadísticas: {str(e)}")
        return {'error': str(e)}