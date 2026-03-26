"""
Servicio para los tres tipos específicos de correos
spme/spme_mensajes/services/correos_especificos_service.py
"""
import logging
from django.utils import timezone
from ..tasks.correos_especificos import (
    enviar_correo_prueba_sistema,
    enviar_correo_solicitud_pendiente,
    enviar_correo_solicitud_aprobada,
    enviar_correo_solicitud_rechazada,
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
    
    # En services/correos_especificos_service.py
    @classmethod
    def notificar_nuevo_mensaje(cls, datos_mensaje, contexto_adicional=None):
        """
        Notifica nuevo mensaje en bandeja (sencillo)
        
        Args:
            datos_mensaje (dict): {
                "destinatarios": [
                    {"email": "a@b.com"},                    # Solo email (requerido)
                    {"email": "c@d.com", "nombre": "Juan"}   # Email + nombre opcional
                ],
                "asunto_mensaje": "Título del mensaje",      # Requerido
                "contenido_mensaje": "Contenido del mensaje", # Requerido
                "remitente_nombre": "Remitente",              # Opcional
                "fecha_envio": datetime,                      # Opcional
                "url_bandeja": "http://..."                   # Opcional
            }
        """
        try:
            # Validaciones de campos requeridos
            if not datos_mensaje.get('destinatarios'):
                raise ValueError("Se requiere destinatarios")
            
            if not datos_mensaje.get('asunto_mensaje'):
                raise ValueError("Se requiere asunto_mensaje")
            
            if not datos_mensaje.get('contenido_mensaje'):
                raise ValueError("Se requiere contenido_mensaje")
            
            # Convertir a lista si es un string (email único)
            if isinstance(datos_mensaje.get('destinatarios'), str):
                datos_mensaje['destinatarios'] = [{
                    'email': datos_mensaje['destinatarios']
                }]
            
            resultados = []
            
            for destinatario in datos_mensaje['destinatarios']:
                # VALIDACIÓN: SOLO EMAIL ES REQUERIDO
                if not destinatario.get('email'):
                    continue  # Saltar destinatarios sin email
                
                # Extraer nombre (opcional) - si no hay, usar parte del email
                email = destinatario['email']
                nombre = destinatario.get('nombre', email.split('@')[0])
                
                # Contexto para el template
                contexto = {
                    'destinatario_nombre': nombre,
                    'destinatario_email': email,
                    'asunto_mensaje': datos_mensaje['asunto_mensaje'],
                    'contenido_mensaje': datos_mensaje['contenido_mensaje'],
                    'remitente_nombre': datos_mensaje.get('remitente_nombre', 'Sistema'),
                    'remitente_email': datos_mensaje.get('remitente_email', ''),
                    'fecha_envio': datos_mensaje.get('fecha_envio', timezone.now()),
                    'url_bandeja': datos_mensaje.get('url_bandeja', '#'),
                    'url_mensaje': datos_mensaje.get('url_mensaje', '#'),
                    'prioridad': datos_mensaje.get('prioridad', 'normal'),
                    'tipo_mensaje': datos_mensaje.get('tipo_mensaje', 'mensaje'),
                    'es_urgente': datos_mensaje.get('prioridad') == 'urgente',
                    'empresa_nombre': contexto_adicional.get('empresa_nombre', 'Nuestra Empresa') if contexto_adicional else 'Nuestra Empresa'
                }
                
                # Agregar contexto adicional si existe
                if contexto_adicional:
                    contexto.update(contexto_adicional)
                
                # Enviar correo usando la tarea existente
                from ..tasks.correos_especificos import enviar_correo_generico
                
                task = enviar_correo_generico.delay(
                    destinatario=email,
                    asunto_template='correos/nuevo_mensaje_asunto.txt',
                    cuerpo_template='correos/nuevo_mensaje_cuerpo.html',
                    contexto=contexto,
                    nombre=nombre
                )
                
                resultados.append({
                    'email': email,
                    'nombre': nombre,
                    'task_id': task.id,
                    'success': True
                })
            
            # Si no hay resultados (todos sin email)
            if not resultados:
                return {
                    'success': False,
                    'error': 'No hay destinatarios válidos (todos sin email)',
                    'resultados': []
                }
            
            return {
                'success': True,
                'resultados': resultados,
                'mensaje': f'Notificaciones enviadas a {len(resultados)} destinatarios'
            }
            
        except Exception as e:
            logger.error(f"Error notificando nuevo mensaje: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'resultados': []
            }
    
    # En services/correos_especificos_service.py
    @staticmethod
    def notificar_solicitud_rechazada(emails_destinatarios, datos_rechazo, contexto_adicional=None):
        """
        Notifica el rechazo de una solicitud
        
        Args:
            emails_destinatarios (str o list): Email(s) de destinatarios
            datos_rechazo (dict): Datos del rechazo
            contexto_adicional (dict): Contexto adicional
        
        Returns:
            dict: Resultado con task_id
        """
        try:
            logger.info(f"Programando notificación de solicitud rechazada")
            
            # Validar datos requeridos
            if not datos_rechazo.get('codigo'):
                raise ValueError("Se requiere código de solicitud")
            
            if not datos_rechazo.get('titulo'):
                raise ValueError("Se requiere título de solicitud")
            
            if not datos_rechazo.get('solicitante_nombre'):
                raise ValueError("Se requiere nombre del solicitante")
            
            # Enviar al task correspondiente
            task = enviar_correo_solicitud_rechazada.delay(
                destinatario=emails_destinatarios,
                datos_rechazo=datos_rechazo,
                contexto_adicional=contexto_adicional
            )
            
            logger.info(f"✅ Notificación de solicitud rechazada programada: {task.id}")
            
            return {
                'success': True,
                'task_id': task.id,
                'solicitud_codigo': datos_rechazo.get('codigo'),
                'tipo': 'solicitud_rechazada',
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error programando notificación rechazo: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'solicitud_codigo': datos_rechazo.get('codigo', 'N/A')
            }