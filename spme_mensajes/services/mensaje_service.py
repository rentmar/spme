#Servicio para manejo de mensajes de usuarios
import logging
import json
from django.utils import timezone
from django.db import transaction
from ..models import MensajeUsuario, TipoMensaje, EstadoMensaje
from ..repositories.mensaje_repository import MensajeRepository
from spme_autenticacion.models import Usuario

logger = logging.getLogger(__name__)

class MensajeService:
    """
    Servicio para operaciones de mensajería interna
    """
    
    @staticmethod
    def obtener_bandeja_entrada(destinatario_id, filtros=None):
        """
        Obtiene la bandeja de entrada de un usuario
        
        Args:
            destinatario_id: ID del usuario destinatario
            filtros: Dict con filtros (estado, tipo, etc.)
        
        Returns:
            Dict con mensajes y estadísticas
        """
        try:
            # Parsear filtros
            filtros = filtros or {}
            estado = filtros.get('estado') if filtros else None
            tipo = filtros.get('tipo') if filtros else None
            limit = filtros.get('limit', 50) if filtros else 50
            offset = filtros.get('offset', 0) if filtros else 0
            
            # Obtener mensajes
            mensajes = MensajeRepository.obtener_mensajes_usuario(
                destinatario_id=destinatario_id,
                estado=estado,
                tipo=tipo,
                limit=limit,
                offset=offset
            )
            
            # Obtener conteos
            conteos = MensajeRepository.contar_mensajes_usuario(
                destinatario_id=destinatario_id,
                estado=estado,
                tipo=tipo
            )
            
            # Formatear respuesta
            return {
                'mensajes': [msg.obtener_datos_contexto() for msg in mensajes],
                'paginacion': {
                    'total': conteos['total'],
                    'limit': limit,
                    'offset': offset,
                    'has_more': (offset + limit) < conteos['total']
                },
                'estadisticas': conteos
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo bandeja para usuario {destinatario_id}: {str(e)}")
            raise
    
    @staticmethod
    def obtener_mensaje(mensaje_id, destinatario_id):
        """
        Obtiene un mensaje específico y lo marca como leído
        
        Args:
            mensaje_id: ID del mensaje
            destinatario_id: ID del usuario
        
        Returns:
            Dict con datos del mensaje
        """
        try:
            mensaje = MensajeRepository.obtener_mensaje_por_id(mensaje_id, destinatario_id)
            
            if not mensaje:
                return None
            
            # Marcar como leído si no lo está
            if mensaje.estado == EstadoMensaje.NO_LEIDO:
                mensaje.marcar_como_leido()
            
            return mensaje.obtener_datos_contexto()
            
        except Exception as e:
            logger.error(f"Error obteniendo mensaje {mensaje_id}: {str(e)}")
            raise
    
    @staticmethod
    def enviar_mensaje_privado(remitente_id, destinatario_id, asunto, contenido, metadata=None):
        """
        Envía un mensaje privado entre usuarios
        
        Args:
            remitente_id: ID del usuario remitente
            destinatario_id: ID del usuario destinatario
            asunto: Asunto del mensaje
            contenido: Contenido del mensaje
            metadata: Metadatos adicionales
        
        Returns:
            Dict con resultado
        """
        try:
            # Preparar datos del mensaje
            mensaje_data = {
                'remitente_id': remitente_id,
                'destinatario_id': destinatario_id,
                'asunto': asunto,
                'contenido': contenido,
                'tipo': TipoMensaje.PRIVADO,
                'prioridad': 1,  # Baja por defecto
                'routing_key': 'mensaje.usuario.privado',
                'metadata': metadata or {},
                'icono': '✉️',
            }
            
            # Crear mensaje directamente (sin Celery para respuesta inmediata)
            mensaje = MensajeRepository.crear_mensaje(mensaje_data)
            
            logger.info(f"Mensaje privado enviado de {remitente_id} a {destinatario_id}")
            
            return {
                'success': True,
                'mensaje_id': mensaje.pk,
                'message_id': mensaje.message_id,
                'tipo': TipoMensaje.PRIVADO
            }
            
        except Exception as e:
            logger.error(f"Error enviando mensaje privado: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def enviar_notificacion_sistema(destinatario_id, contenido, asunto=None, prioridad=1, metadata=None):
        """
        Envía una notificación del sistema a un usuario
        
        Args:
            destinatario_id: ID del usuario
            contenido: Contenido de la notificación
            asunto: Asunto (opcional)
            prioridad: Prioridad (1=Baja, 2=Media, 3=Alta)
            metadata: Metadatos adicionales
        
        Returns:
            Dict con resultado
        """
        try:
            mensaje_data = {
                'destinatario_id': destinatario_id,
                'remitente_id': None,  # Sistema
                'asunto': asunto or 'Notificación del Sistema',
                'contenido': contenido,
                'tipo': TipoMensaje.SISTEMA,
                'prioridad': prioridad,
                'routing_key': 'mensaje.usuario.sistema',
                'metadata': metadata or {},
                'icono': '🔔',
            }
            
            mensaje = MensajeRepository.crear_mensaje(mensaje_data)
            
            logger.info(f"Notificación del sistema enviada a {destinatario_id}")
            
            return {
                'success': True,
                'mensaje_id': mensaje.pk,
                'message_id': mensaje.message_id,
                'tipo': TipoMensaje.SISTEMA
            }
            
        except Exception as e:
            logger.error(f"Error enviando notificación del sistema: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def enviar_alerta_actividad(destinatario_id, actividad_id, tipo_evento, datos_actividad):
        """
        Envía una alerta relacionada con actividades
        
        Args:
            destinatario_id: ID del usuario
            actividad_id: ID de la actividad
            tipo_evento: Tipo de evento (inicio_inminente, retraso, etc.)
            datos_actividad: Datos adicionales de la actividad
        
        Returns:
            Dict con resultado
        """
        try:
            # Mapear tipo de evento a tipo de mensaje
            evento_tipo_map = {
                'inicio_inminente': TipoMensaje.RECORDATORIO,
                'retraso': TipoMensaje.RETRASO,
                'reprogramacion': TipoMensaje.REPROGRAMACION,
                'recordatorio': TipoMensaje.RECORDATORIO,
                'completado': TipoMensaje.SISTEMA,
                'actualizacion': TipoMensaje.SISTEMA,
            }
            
            tipo_mensaje = evento_tipo_map.get(tipo_evento, TipoMensaje.SISTEMA)
            
            # Mapear prioridad
            evento_prioridad = {
                'inicio_inminente': 2,  # Media
                'retraso': 3,           # Alta
                'reprogramacion': 2,    # Media
                'recordatorio': 1,      # Baja
                'completado': 1,        # Baja
                'actualizacion': 1,     # Baja
            }
            
            prioridad = evento_prioridad.get(tipo_evento, 1)
            
            # Generar contenido
            contenido = f"Actividad: {datos_actividad.get('nombre', 'Actividad')}\n"
            contenido += f"Evento: {tipo_evento}\n"
            if datos_actividad.get('fecha'):
                contenido += f"Fecha: {datos_actividad['fecha']}\n"
            if datos_actividad.get('mensaje'):
                contenido += f"\n{datos_actividad['mensaje']}"
            
            mensaje_data = {
                'destinatario_id': destinatario_id,
                'remitente_id': None,
                'asunto': datos_actividad.get('asunto', f"Actividad: {tipo_evento}"),
                'contenido': contenido,
                'tipo': tipo_mensaje,
                'prioridad': prioridad,
                'routing_key': 'mensaje.usuario.actividad',
                'metadata': {
                    'actividad_id': actividad_id,
                    'tipo_evento': tipo_evento,
                    **datos_actividad.get('metadata', {})
                },
                'referencia_id': f"ACT-{actividad_id}",
                'accion_url': datos_actividad.get('url', ''),
                'accion_texto': datos_actividad.get('accion_texto', 'Ver Actividad'),
                'icono': datos_actividad.get('icono', '📅'),
                'actividad_id': actividad_id,
                'proyecto_id': datos_actividad.get('proyecto_id'),
            }
            
            mensaje = MensajeRepository.crear_mensaje(mensaje_data)
            
            logger.info(f"Alerta de actividad {actividad_id} enviada a {destinatario_id}")
            
            return {
                'success': True,
                'mensaje_id': mensaje.pk,
                'message_id': mensaje.message_id,
                'tipo': tipo_mensaje,
                'tipo_evento': tipo_evento
            }
            
        except Exception as e:
            logger.error(f"Error enviando alerta de actividad: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def actualizar_estado_mensaje(mensaje_id, destinatario_id, nuevo_estado):
        """
        Actualiza el estado de un mensaje
        
        Args:
            mensaje_id: ID del mensaje
            destinatario_id: ID del usuario
            nuevo_estado: Nuevo estado
        
        Returns:
            Mensaje actualizado o None
        """
        try:
            return MensajeRepository.actualizar_estado_mensaje(
                mensaje_id=mensaje_id,
                nuevo_estado=nuevo_estado,
                destinatario_id=destinatario_id
            )
            
        except Exception as e:
            logger.error(f"Error actualizando estado de mensaje {mensaje_id}: {str(e)}")
            raise
    
    @staticmethod
    def marcar_varios_como_leido(mensaje_ids, destinatario_id):
        """
        Marca varios mensajes como leídos
        
        Args:
            mensaje_ids: Lista de IDs de mensajes
            destinatario_id: ID del usuario
        
        Returns:
            Número de mensajes actualizados
        """
        try:
            return MensajeRepository.marcar_varios_como_leido(mensaje_ids, destinatario_id)
            
        except Exception as e:
            logger.error(f"Error marcando mensajes como leídos: {str(e)}")
            raise
    
    @staticmethod
    def buscar_mensajes(destinatario_id, query, limit=20):
        """
        Busca mensajes por contenido
        
        Args:
            destinatario_id: ID del usuario
            query: Texto de búsqueda
            limit: Límite de resultados
        
        Returns:
            Lista de mensajes encontrados
        """
        try:
            mensajes = MensajeRepository.buscar_mensajes(destinatario_id, query, limit)
            return [msg.obtener_datos_contexto() for msg in mensajes]
            
        except Exception as e:
            logger.error(f"Error buscando mensajes para usuario {destinatario_id}: {str(e)}")
            raise
    
    @staticmethod
    def obtener_estadisticas(destinatario_id):
        """
        Obtiene estadísticas de mensajes del usuario
        
        Args:
            destinatario_id: ID del usuario
        
        Returns:
            Dict con estadísticas
        """
        try:
            return MensajeRepository.contar_mensajes_usuario(destinatario_id)
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas para usuario {destinatario_id}: {str(e)}")
            raise
    
    @staticmethod
    def obtener_mensajes_por_actividad(actividad_id, destinatario_id=None):
        """
        Obtiene mensajes relacionados con una actividad
        
        Args:
            actividad_id: ID de la actividad
            destinatario_id: ID del usuario (opcional)
        
        Returns:
            Lista de mensajes
        """
        try:
            mensajes = MensajeRepository.obtener_mensajes_por_actividad(actividad_id, destinatario_id)
            return [msg.obtener_datos_contexto() for msg in mensajes]
            
        except Exception as e:
            logger.error(f"Error obteniendo mensajes para actividad {actividad_id}: {str(e)}")
            raise
    
    @staticmethod
    def obtener_mensajes_por_proyecto(proyecto_id, destinatario_id=None):
        """
        Obtiene mensajes relacionados con un proyecto
        
        Args:
            proyecto_id: ID del proyecto
            destinatario_id: ID del usuario (opcional)
        
        Returns:
            Lista de mensajes
        """
        try:
            mensajes = MensajeRepository.obtener_mensajes_por_proyecto(proyecto_id, destinatario_id)
            return [msg.obtener_datos_contexto() for msg in mensajes]
            
        except Exception as e:
            logger.error(f"Error obteniendo mensajes para proyecto {proyecto_id}: {str(e)}")
            raise