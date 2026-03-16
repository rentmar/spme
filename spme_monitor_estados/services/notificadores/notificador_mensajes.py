# services/notificadores/notificador_mensajes.py
# Propósito: Notificaciones internas (inmediatas) usando spme_mensajes
# Los mensajes se crean directamente en la BD y aparecen en la bandeja del usuario

from django.utils import timezone
from datetime import timedelta
import logging

from spme_mensajes.models import MensajeUsuario, TipoMensaje
from .notificador_base import NotificadorBase

logger = logging.getLogger(__name__)

class NotificadorMensajes(NotificadorBase):
    """
    Notificador de mensajes internos (INMEDIATO)
    
    Este notificador crea mensajes en la tabla spme_mensajes_mensajesusuario
    que aparecen inmediatamente en la bandeja del usuario.
    """
    
    def __init__(self, config):
        """
        Inicializa el notificador con la configuración de la entidad
        
        Args:
            config: Objeto ConfiguracionMonitoreo
        """
        self.config = config
    
    def notificar(self, tipo_entidad, evento, entidad, contexto=None):
        """
        Crea un mensaje interno inmediatamente.
        
        Args:
            tipo_entidad: Tipo de entidad (actividad, tarea, etc.)
            evento: Evento ocurrido
            entidad: La entidad relacionada
            contexto: Datos adicionales
            
        Returns:
            MensajeUsuario creado o None si no aplica
        """
        # Verificar si las notificaciones internas están activadas
        if not self.config.notificaciones_internas:
            return None
        
        # Obtener el responsable (destinatario)
        responsable = self._obtener_responsable(tipo_entidad, entidad)
        if not responsable or not responsable.email:
            logger.warning(f"⚠️ Sin responsable para {tipo_entidad} {getattr(entidad, 'codigo', '')}")
            return None
        
        try:
            # Generar asunto según tipo y evento
            asunto = self._generar_asunto(tipo_entidad, evento, entidad)
            
            # Generar contenido según tipo y evento
            contenido = self._generar_contenido(tipo_entidad, evento, entidad, contexto)
            
            # Determinar tipo de mensaje según evento
            tipo_mensaje = self._obtener_tipo_mensaje(evento)
            
            # Determinar icono según evento
            icono = self._obtener_icono(evento)
            
            # Crear el mensaje en la BD
            mensaje = MensajeUsuario.objects.create(
                destinatario=responsable,
                remitente=None,  # None = mensaje del sistema
                tipo=tipo_mensaje,
                prioridad=self.config.prioridad_notificacion,
                icono=icono,
                asunto=asunto,
                contenido=contenido,
                fecha_expiracion=timezone.now() + timedelta(days=30),  # 30 días de vigencia
                actividad_id=entidad.id if tipo_entidad == 'actividad' else None,
                metadata={
                    'tipo_notificacion': 'evento',
                    'tipo_entidad': tipo_entidad,
                    'evento': evento,
                    'entidad_id': entidad.id,
                    'entidad_codigo': getattr(entidad, 'codigo', ''),
                    'fecha': str(timezone.now().date())
                }
            )
            
            logger.info(f"📨 Mensaje interno para {responsable.email}: {asunto}")
            return mensaje
            
        except Exception as e:
            logger.error(f"❌ Error creando mensaje interno: {e}")
            return None
    
    def _obtener_responsable(self, tipo_entidad, entidad):
        """
        Obtiene el responsable según el tipo de entidad
        """
        if tipo_entidad == 'actividad':
            return getattr(entidad, 'responsable', None)
        elif tipo_entidad == 'tarea':
            if hasattr(entidad, 'actividad') and entidad.actividad:
                return getattr(entidad.actividad, 'responsable', None)
        elif tipo_entidad == 'actividad_pei':
            return getattr(entidad, 'responsable', None)
        elif tipo_entidad == 'tarea_pei':
            if hasattr(entidad, 'actividad') and entidad.actividad:
                return getattr(entidad.actividad, 'responsable', None)
        return None
    
    def _generar_asunto(self, tipo_entidad, evento, entidad):
        """
        Genera el asunto del mensaje según tipo y evento
        """
        codigo = getattr(entidad, 'codigo', '')
        
        asuntos = {
            ('actividad', 'reprogramacion'): f"📅 Actividad requiere reprogramación: {codigo}",
            ('actividad', 'reporte'): f"📋 Reporte requerido: {codigo}",
            ('actividad', 'inicio'): f"🚀 Actividad iniciada: {codigo}",
            ('actividad', 'retraso'): f"⚠️ Retraso en actividad: {codigo}",
            ('actividad', 'retraso_critico'): f"🔴 RETRASO CRÍTICO: {codigo}",
            ('tarea', 'vencida'): f"⚠️ Tarea vencida: {codigo}",
            ('actividad_pei', 'inicio'): f"🎯 Actividad PEI iniciada: {codigo}",
            ('actividad_pei', 'retraso'): f"⚠️ Retraso en actividad PEI: {codigo}",
            ('actividad_pei', 'retraso_critico'): f"🔴 RETRASO CRÍTICO en actividad PEI: {codigo}",
            ('actividad_pei', 'reprogramacion'): f"📅 Actividad PEI requiere reprogramación: {codigo}",
            ('actividad_pei', 'reporte'): f"📋 Reporte requerido para actividad PEI: {codigo}",
        }
        return asuntos.get((tipo_entidad, evento), f"Notificación: {codigo}")
    
    def _generar_contenido(self, tipo_entidad, evento, entidad, contexto):
        """
        Genera el contenido del mensaje
        """
        nombre = getattr(entidad, 'nombreCorto', getattr(entidad, 'titulo', ''))
        codigo = getattr(entidad, 'codigo', '')
        dias = contexto.get('dias') if contexto else None
        
        if evento == 'reprogramacion':
            return (f"La actividad {nombre} ({codigo}) ha sido reprogramada "
                   f"automáticamente por retraso de {dias} días y falta de formularios.")
        elif evento == 'reporte':
            return f"La actividad {nombre} ({codigo}) requiere la presentación de un informe."
        elif evento == 'vencida':
            return f"La tarea {nombre} ({codigo}) está vencida por {dias} días."
        elif evento == 'inicio':
            return f"La actividad {nombre} ({codigo}) ha iniciado su ejecución."
        elif evento == 'retraso':
            return f"La actividad {nombre} ({codigo}) tiene un retraso de {dias} días."
        elif evento == 'retraso_critico':
            return (f"🚨 ALERTA CRÍTICA: La actividad {nombre} ({codigo}) tiene "
                   f"un retraso de {dias} días. Se requiere acción inmediata.")
        
        return "Notificación del sistema"
    
    def _obtener_tipo_mensaje(self, evento):
        """
        Mapea eventos a tipos de mensaje del modelo MensajeUsuario
        """
        tipos = {
            'reprogramacion': TipoMensaje.REPROGRAMACION,
            'retraso': TipoMensaje.RETRASO,
            'retraso_critico': TipoMensaje.RETRASO,
            'reporte': TipoMensaje.RECORDATORIO,
            'inicio': TipoMensaje.SISTEMA,
            'vencida': TipoMensaje.ALERTA,
        }
        return tipos.get(evento, TipoMensaje.SISTEMA)
    
    def _obtener_icono(self, evento):
        """
        Obtiene el icono según el evento
        """
        iconos = {
            'reprogramacion': '📅',
            'retraso': '⚠️',
            'retraso_critico': '🔴',
            'reporte': '📋',
            'inicio': '🚀',
            'vencida': '⚠️',
        }
        return iconos.get(evento, '📧')