# services/notificadores/notificador_email_lotes.py
# Propósito: Notificaciones por email con procesamiento por lotes
# NO envía directamente, SOLO encola en la BD para procesamiento posterior

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import logging

from ...models.cola_email import EmailEnCola
from .notificador_base import NotificadorBase

logger = logging.getLogger(__name__)

class NotificadorEmailLotes(NotificadorBase):
    """
    Notificador de emails con procesamiento por lotes
    
    Características:
    - Encola emails en BD en lugar de enviarlos inmediatamente
    - Asigna prioridad según configuración
    - Programa envío según prioridad (inmediato, 5min, 15min, 30min)
    - Los emails son procesados por una tarea Beat separada
    """
    
    def __init__(self, config):
        """
        Inicializa el notificador con la configuración de la entidad
        
        Args:
            config: Objeto ConfiguracionMonitoreo
        """
        self.config = config
        self.site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    
    def notificar(self, tipo_entidad, evento, entidad, contexto=None):
        """
        Encola un email para envío posterior por lotes.
        
        NO envía inmediatamente, solo guarda en BD con estado 'pendiente'.
        
        Args:
            tipo_entidad: Tipo de entidad
            evento: Evento ocurrido
            entidad: La entidad relacionada
            contexto: Datos adicionales
            
        Returns:
            EmailEnCola creado o None
        """
        # Verificar si las notificaciones email están activadas
        if not self.config.notificaciones_email:
            return None
        
        # Obtener el responsable (destinatario)
        responsable = self._obtener_responsable(tipo_entidad, entidad)
        if not responsable or not responsable.email:
            logger.warning(f"⚠️ Sin responsable para {tipo_entidad} {getattr(entidad, 'codigo', '')}")
            return None
        
        try:
            # Generar asunto
            asunto = self._generar_asunto(tipo_entidad, evento, entidad)
            
            # Preparar contexto para las plantillas HTML
            contexto_completo = {
                'entidad': entidad,
                'responsable': responsable,
                'fecha': timezone.now().strftime('%d/%m/%Y %H:%M'),
                'dias': contexto.get('dias') if contexto else None,
                'site_url': self.site_url,
                'tipo_entidad': tipo_entidad,
                'evento': evento,
                **(contexto or {})
            }
            
            # Intentar renderizar plantilla HTML (si no existe, usar texto plano)
            try:
                html_content = render_to_string(
                    f'emails/{tipo_entidad}_{evento}.html',
                    contexto_completo
                )
                text_content = strip_tags(html_content)
            except:
                # Si no hay plantilla, usar contenido básico
                text_content = self._generar_contenido_texto(tipo_entidad, evento, entidad, contexto)
                html_content = f"<p>{text_content.replace(chr(10), '<br>')}</p>"
            
            # Calcular cuándo debe enviarse según prioridad
            programado_para = self._calcular_programacion(self.config.prioridad_notificacion)
            
            # Guardar en BD (NO enviar todavía)
            email_cola = EmailEnCola.objects.create(
                destinatario=responsable.email,
                asunto=asunto,
                cuerpo_html=html_content,
                cuerpo_texto=text_content,
                prioridad=self.config.prioridad_notificacion,
                tipo_entidad=tipo_entidad,
                entidad_id=entidad.id,
                evento=evento,
                programado_para=programado_para
            )
            
            logger.info(f"📧 Email ENCOLADO para {responsable.email}: {asunto} (prioridad {self.config.prioridad_notificacion})")
            return email_cola
            
        except Exception as e:
            logger.error(f"❌ Error encolando email: {e}")
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
        Genera el asunto del email
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
        return asuntos.get((tipo_entidad, evento), f"Notificación del sistema: {codigo}")
    
    def _generar_contenido_texto(self, tipo_entidad, evento, entidad, contexto):
        """
        Genera contenido en texto plano (fallback si no hay plantilla)
        """
        nombre = getattr(entidad, 'nombreCorto', getattr(entidad, 'titulo', ''))
        codigo = getattr(entidad, 'codigo', '')
        dias = contexto.get('dias') if contexto else None
        
        if evento == 'reprogramacion':
            return (f"La actividad {nombre} ({codigo}) ha sido reprogramada "
                   f"automáticamente por retraso de {dias} días.")
        elif evento == 'reporte':
            return f"La actividad {nombre} ({codigo}) requiere la presentación de un informe."
        elif evento == 'vencida':
            return f"La tarea {nombre} ({codigo}) está vencida por {dias} días."
        elif evento == 'inicio':
            return f"La actividad {nombre} ({codigo}) ha iniciado su ejecución."
        elif evento == 'retraso':
            return f"La actividad {nombre} ({codigo}) tiene un retraso de {dias} días."
        elif evento == 'retraso_critico':
            return (f"ALERTA CRÍTICA: La actividad {nombre} ({codigo}) tiene "
                   f"un retraso de {dias} días. Se requiere acción inmediata.")
        
        return "Notificación automática del sistema"
    
    def _calcular_programacion(self, prioridad):
        """
        Calcula cuándo debe enviarse el email según prioridad
        
        Args:
            prioridad: 1 (Baja) a 4 (Crítica)
            
        Returns:
            datetime: Cuándo programar el envío
        """
        ahora = timezone.now()
        
        if prioridad >= 4:      # Crítica
            return ahora        # Inmediato
        elif prioridad == 3:     # Alta
            return ahora + timedelta(minutes=5)    # 5 minutos
        elif prioridad == 2:     # Media
            return ahora + timedelta(minutes=15)   # 15 minutos
        else:                    # Baja
            return ahora + timedelta(minutes=30)   # 30 minutos