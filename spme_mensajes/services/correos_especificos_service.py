"""
Servicio para los tres tipos específicos de correos
"""
import logging
from django.utils import timezone
from ..tasks.correos_especificos import (
    enviar_correo_prueba_sistema,
    enviar_correo_solicitud_pendiente,
    enviar_correo_solicitud_aprobada,
)

logger = logging.getLogger(__name__)

class CorreosEspecificosService:
    """
    Servicio para manejar los tres tipos específicos de correos
    """
    
    @staticmethod
    def enviar_prueba_sistema(email, nombre_usuario=None, contexto_adicional=None):
        """
        Envía correo de prueba del sistema
        
        Args:
            email (str): Email del destinatario
            nombre_usuario (str): Nombre del usuario
            contexto_adicional (dict): Contexto adicional para la plantilla
        
        Returns:
            dict: Resultado con task_id
        """
        try:
            logger.info(f"Programando correo de prueba para {email}")
            
            task = enviar_correo_prueba_sistema.delay(
                destinatario=email,
                nombre_usuario=nombre_usuario,
                contexto_adicional=contexto_adicional
            )
            
            logger.info(f"✅ Correo de prueba programado: {task.id}")
            
            return {
                'success': True,
                'task_id': task.id,
                'email': email,
                'tipo': 'prueba_sistema',
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error programando correo de prueba: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'email': email
            }
    
    @staticmethod
    def notificar_solicitud_pendiente(emails_revisores, datos_solicitud, contexto_adicional=None):
        """
        Notifica a revisores sobre solicitud pendiente
        
        Args:
            emails_revisores (str o list): Email(s) del revisor(es)
            datos_solicitud (dict): Datos de la solicitud
            contexto_adicional (dict): Contexto adicional
        
        Returns:
            dict: Resultado con task_id
        """
        try:
            logger.info(f"Programando notificación de solicitud pendiente")
            
            task = enviar_correo_solicitud_pendiente.delay(
                destinatario=emails_revisores,
                datos_solicitud=datos_solicitud,
                contexto_adicional=contexto_adicional
            )
            
            logger.info(f"✅ Notificación de solicitud pendiente programada: {task.id}")
            
            return {
                'success': True,
                'task_id': task.id,
                'solicitud_codigo': datos_solicitud.get('codigo'),
                'tipo': 'solicitud_pendiente',
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error programando notificación pendiente: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'solicitud_codigo': datos_solicitud.get('codigo', 'N/A')
            }
    
    @staticmethod
    def notificar_solicitud_aprobada(emails_destinatarios, datos_aprobacion, contexto_adicional=None):
        """
        Notifica aprobación de solicitud
        
        Args:
            emails_destinatarios (str o list): Email(s) de destinatarios
            datos_aprobacion (dict): Datos de la aprobación
            contexto_adicional (dict): Contexto adicional
        
        Returns:
            dict: Resultado con task_id
        """
        try:
            logger.info(f"Programando notificación de solicitud aprobada")
            
            task = enviar_correo_solicitud_aprobada.delay(
                destinatario=emails_destinatarios,
                datos_aprobacion=datos_aprobacion,
                contexto_adicional=contexto_adicional
            )
            
            logger.info(f"✅ Notificación de solicitud aprobada programada: {task.id}")
            
            return {
                'success': True,
                'task_id': task.id,
                'solicitud_codigo': datos_aprobacion.get('codigo'),
                'tipo': 'solicitud_aprobada',
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error programando notificación aprobada: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'solicitud_codigo': datos_aprobacion.get('codigo', 'N/A')
            }
    
    @staticmethod
    def ejemplo_solicitud_pendiente():
        """
        Retorna ejemplo de datos para solicitud pendiente
        """
        return {
            'codigo': 'SOL-2024-001',
            'titulo': 'Solicitud de recursos adicionales para proyecto X',
            'solicitante': 'Juan Pérez',
            'fecha_solicitud': timezone.now(),
            'tipo': 'Recursos Humanos',
            'prioridad': 'alta',
            'plazo_revision': timezone.now().replace(hour=23, minute=59, second=59),
            'descripcion': 'Se requieren 2 desarrolladores adicionales para cumplir con los plazos del proyecto.',
            'url_revision': 'http://localhost:8000/solicitudes/SOL-2024-001/revisar',
        }
    
    @staticmethod
    def ejemplo_solicitud_aprobada():
        """
        Retorna ejemplo de datos para solicitud aprobada
        """
        return {
            'codigo': 'SOL-2024-001',
            'titulo': 'Solicitud de recursos adicionales para proyecto X',
            'solicitante_nombre': 'Juan Pérez',
            'aprobador_nombre': 'María González',
            'fecha_aprobacion': timezone.now(),
            'numero_aprobacion': 'APR-2024-015',
            'observaciones': 'Aprobado con la condición de presentar informe semanal de avance.',
            'proximos_pasos': '1. Contactar al departamento de RRHH\n2. Programar entrevistas\n3. Realizar onboarding',
            'url_detalles': 'http://localhost:8000/solicitudes/SOL-2024-001',
            'url_siguiente_paso': 'http://localhost:8000/proyectos/X/recursos',
            'siguiente_fase': 'Contratación',
            'responsable_siguiente': 'Departamento de RRHH',
            'fecha_limite': timezone.now().replace(day=timezone.now().day + 7),
        }