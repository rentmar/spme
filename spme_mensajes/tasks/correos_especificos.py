"""
Tareas específicas para los tres tipos de correos solicitados
"""
from celery import shared_task
import logging
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

# ============================================================================
# 1. CORREO DE PRUEBA DEL SISTEMA
# ============================================================================

@shared_task(
    bind=True,
    name="correo.enviar_prueba_sistema",
    queue='correo',
    priority=5,
    routing_key='notificacion.correo.prueba'
)
def enviar_correo_prueba_sistema(self, destinatario, nombre_usuario=None, contexto_adicional=None):
    """
    Envía correo de prueba del sistema
    
    Args:
        destinatario (str): Email del destinatario
        nombre_usuario (str): Nombre del usuario
        contexto_adicional (dict): Contexto adicional para la plantilla
    
    Returns:
        dict: Resultado del envío
    """
    task_id = self.request.id
    
    try:
        logger.info(f"[{task_id}] Enviando correo de prueba a {destinatario}")
        
        # 1. Preparar contexto para la plantilla
        contexto = {
            'nombre_usuario': nombre_usuario or 'Usuario del Sistema',
            'email': destinatario,
            'fecha_hora': timezone.now(),
            'task_id': task_id,
            'app_url': getattr(settings, 'APP_URL', 'http://localhost:8000'),
            'support_url': getattr(settings, 'SUPPORT_URL', 'mailto:soporte@spme.com'),
            'privacy_url': getattr(settings, 'PRIVACY_URL', '#'),
            'referencia_id': f"TEST-{task_id[:8].upper()}",
            'version': getattr(settings, 'APP_VERSION', '1.0.0'),
            'entorno': getattr(settings, 'ENVIRONMENT', 'Desarrollo'),
        }
        
        # Agregar contexto adicional si se proporciona
        if contexto_adicional:
            contexto.update(contexto_adicional)
        
        # 2. Renderizar plantilla HTML
        html_content = render_to_string('correos/prueba_sistema.html', contexto)
        text_content = strip_tags(html_content)
        
        # 3. Enviar correo
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@spme.com')
        subject = f"🧪 Prueba del Sistema SPME - {timezone.now().strftime('%d/%m/%Y')}"
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[destinatario],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        logger.info(f"[{task_id}] ✅ Correo de prueba enviado a {destinatario}")
        
        return {
            'success': True,
            'task_id': task_id,
            'destinatario': destinatario,
            'tipo': 'prueba_sistema',
            'plantilla': 'prueba_sistema.html',
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        error_msg = f"Error enviando correo de prueba: {str(e)}"
        logger.error(f"[{task_id}] ❌ {error_msg}")
        return {
            'success': False,
            'task_id': task_id,
            'error': error_msg,
            'tipo': 'prueba_sistema'
        }

# ============================================================================
# 2. CORREO DE SOLICITUD PENDIENTE DE APROBACIÓN
# ============================================================================

@shared_task(
    bind=True,
    name="correo.enviar_solicitud_pendiente",
    queue='correo',
    priority=8,
    routing_key='notificacion.correo.solicitud.pendiente'
)
def enviar_correo_solicitud_pendiente(self, destinatario, datos_solicitud, contexto_adicional=None):
    """
    Envía correo de solicitud pendiente de aprobación
    
    Args:
        destinatario (str o list): Email(s) del revisor(es)
        datos_solicitud (dict): Datos de la solicitud
        contexto_adicional (dict): Contexto adicional para la plantilla
    
    Returns:
        dict: Resultado del envío
    """
    task_id = self.request.id
    
    try:
        # Convertir a lista si es un solo email
        if isinstance(destinatario, str):
            destinatarios = [destinatario]
        else:
            destinatarios = destinatario
        
        logger.info(f"[{task_id}] Enviando notificación de solicitud pendiente a {len(destinatarios)} revisores")
        
        # 1. Preparar contexto base
        contexto_base = {
            'app_url': getattr(settings, 'APP_URL', 'http://localhost:8000'),
            'support_url': getattr(settings, 'SUPPORT_URL', 'mailto:soporte@spme.com'),
            'privacy_url': getattr(settings, 'PRIVACY_URL', '#'),
            'referencia_id': datos_solicitud.get('solicitud_codigo', f"SOL-{task_id[:8].upper()}"),
        }
        
        resultados = []
        
        # 2. Enviar a cada destinatario
        for destinatario_email in destinatarios:
            try:
                # 3. Preparar contexto específico para este destinatario
                contexto = contexto_base.copy()
                contexto.update({
                    'nombre_revisor': datos_solicitud.get('nombre_revisor', 'Revisor'),
                    'email': destinatario_email,
                    'task_id': task_id,
                    'fecha_envio': timezone.now(),
                    
                    # Datos de la solicitud
                    'solicitud_codigo': datos_solicitud.get('codigo', 'N/A'),
                    'titulo_solicitud': datos_solicitud.get('titulo', 'Solicitud sin título'),
                    'nombre_solicitante': datos_solicitud.get('solicitante', 'Usuario'),
                    'fecha_solicitud': datos_solicitud.get('fecha_solicitud', timezone.now()),
                    'tipo_solicitud': datos_solicitud.get('tipo', 'General'),
                    'prioridad': datos_solicitud.get('prioridad', 'media'),
                    'plazo_revision': datos_solicitud.get('plazo_revision'),
                    'descripcion': datos_solicitud.get('descripcion', ''),
                    'url_revision': datos_solicitud.get('url_revision', contexto_base['app_url']),
                })
                
                # Agregar contexto adicional si se proporciona
                if contexto_adicional:
                    contexto.update(contexto_adicional)
                
                # 4. Renderizar plantilla HTML
                html_content = render_to_string('correos/solicitud_pendiente.html', contexto)
                text_content = strip_tags(html_content)
                
                # 5. Preparar asunto
                asunto = f"⏳ Solicitud Pendiente: {contexto['solicitud_codigo']} - {contexto['titulo_solicitud'][:50]}..."
                if len(contexto['titulo_solicitud']) > 50:
                    asunto = f"⏳ Solicitud Pendiente: {contexto['solicitud_codigo']} - {contexto['titulo_solicitud'][:50]}..."
                
                # 6. Enviar correo
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@spme.com')
                
                email = EmailMultiAlternatives(
                    subject=asunto,
                    body=text_content,
                    from_email=from_email,
                    to=[destinatario_email],
                )
                email.attach_alternative(html_content, "text/html")
                email.send()
                
                logger.debug(f"[{task_id}] ✓ Notificación enviada a {destinatario_email}")
                
                resultados.append({
                    'destinatario': destinatario_email,
                    'estado': 'enviado',
                    'error': None
                })
                
            except Exception as e:
                error_msg = f"Error con destinatario {destinatario_email}: {str(e)}"
                logger.warning(f"[{task_id}] ⚠️  {error_msg}")
                
                resultados.append({
                    'destinatario': destinatario_email,
                    'estado': 'error',
                    'error': str(e)
                })
        
        # 7. Calcular estadísticas
        enviados = sum(1 for r in resultados if r['estado'] == 'enviado')
        errores = sum(1 for r in resultados if r['estado'] == 'error')
        
        logger.info(f"[{task_id}] ✅ Notificaciones de solicitud pendiente: {enviados} enviados, {errores} errores")
        
        return {
            'success': True,
            'task_id': task_id,
            'total_destinatarios': len(destinatarios),
            'enviados': enviados,
            'errores': errores,
            'resultados': resultados,
            'solicitud_codigo': datos_solicitud.get('codigo'),
            'tipo': 'solicitud_pendiente',
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        error_msg = f"Error en envío de solicitud pendiente: {str(e)}"
        logger.error(f"[{task_id}] ❌ {error_msg}")
        return {
            'success': False,
            'task_id': task_id,
            'error': error_msg,
            'tipo': 'solicitud_pendiente'
        }

# ============================================================================
# 3. CORREO DE SOLICITUD APROBADA
# ============================================================================

@shared_task(
    bind=True,
    name="correo.enviar_solicitud_aprobada",
    queue='correo',
    priority=9,
    routing_key='notificacion.correo.solicitud.aprobada'
)
def enviar_correo_solicitud_aprobada(self, destinatario, datos_aprobacion, contexto_adicional=None):
    """
    Envía correo de solicitud aprobada
    
    Args:
        destinatario (str o list): Email(s) del solicitante y otros interesados
        datos_aprobacion (dict): Datos de la aprobación
        contexto_adicional (dict): Contexto adicional para la plantilla
    
    Returns:
        dict: Resultado del envío
    """
    task_id = self.request.id
    
    try:
        # Convertir a lista si es un solo email
        if isinstance(destinatario, str):
            destinatarios = [destinatario]
        else:
            destinatarios = destinatario
        
        logger.info(f"[{task_id}] Enviando notificación de solicitud aprobada a {len(destinatarios)} destinatarios")
        
        # 1. Preparar contexto base
        contexto_base = {
            'app_url': getattr(settings, 'APP_URL', 'http://localhost:8000'),
            'support_url': getattr(settings, 'SUPPORT_URL', 'mailto:soporte@spme.com'),
            'privacy_url': getattr(settings, 'PRIVACY_URL', '#'),
            'referencia_id': datos_aprobacion.get('solicitud_codigo', f"APR-{task_id[:8].upper()}"),
        }
        
        resultados = []
        
        # 2. Enviar a cada destinatario
        for destinatario_email in destinatarios:
            try:
                # 3. Preparar contexto específico
                contexto = contexto_base.copy()
                contexto.update({
                    'nombre_solicitante': datos_aprobacion.get('solicitante_nombre', 'Solicitante'),
                    'email': destinatario_email,
                    'task_id': task_id,
                    'fecha_envio': timezone.now(),
                    
                    # Datos de la aprobación
                    'solicitud_codigo': datos_aprobacion.get('codigo', 'N/A'),
                    'titulo_solicitud': datos_aprobacion.get('titulo', 'Solicitud sin título'),
                    'nombre_aprobador': datos_aprobacion.get('aprobador_nombre', 'Aprobador'),
                    'fecha_aprobacion': datos_aprobacion.get('fecha_aprobacion', timezone.now()),
                    'numero_aprobacion': datos_aprobacion.get('numero_aprobacion'),
                    'observaciones': datos_aprobacion.get('observaciones', ''),
                    'proximos_pasos': datos_aprobacion.get('proximos_pasos', ''),
                    'url_detalles': datos_aprobacion.get('url_detalles', contexto_base['app_url']),
                    'url_siguiente_paso': datos_aprobacion.get('url_siguiente_paso'),
                    'siguiente_fase': datos_aprobacion.get('siguiente_fase', 'Implementación'),
                    'responsable_siguiente': datos_aprobacion.get('responsable_siguiente', 'Equipo correspondiente'),
                    'fecha_limite': datos_aprobacion.get('fecha_limite'),
                })
                
                # Agregar contexto adicional si se proporciona
                if contexto_adicional:
                    contexto.update(contexto_adicional)
                
                # 4. Renderizar plantilla HTML
                html_content = render_to_string('correos/solicitud_aprobada.html', contexto)
                text_content = strip_tags(html_content)
                
                # 5. Preparar asunto
                asunto = f"✅ Solicitud Aprobada: {contexto['solicitud_codigo']} - {contexto['titulo_solicitud'][:50]}..."
                if len(contexto['titulo_solicitud']) > 50:
                    asunto = f"✅ Solicitud Aprobada: {contexto['solicitud_codigo']} - {contexto['titulo_solicitud'][:50]}..."
                
                # 6. Enviar correo
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@spme.com')
                
                email = EmailMultiAlternatives(
                    subject=asunto,
                    body=text_content,
                    from_email=from_email,
                    to=[destinatario_email],
                )
                email.attach_alternative(html_content, "text/html")
                email.send()
                
                logger.debug(f"[{task_id}] ✓ Notificación de aprobación enviada a {destinatario_email}")
                
                resultados.append({
                    'destinatario': destinatario_email,
                    'estado': 'enviado',
                    'error': None
                })
                
            except Exception as e:
                error_msg = f"Error con destinatario {destinatario_email}: {str(e)}"
                logger.warning(f"[{task_id}] ⚠️  {error_msg}")
                
                resultados.append({
                    'destinatario': destinatario_email,
                    'estado': 'error',
                    'error': str(e)
                })
        
        # 7. Calcular estadísticas
        enviados = sum(1 for r in resultados if r['estado'] == 'enviado')
        errores = sum(1 for r in resultados if r['estado'] == 'error')
        
        logger.info(f"[{task_id}] ✅ Notificaciones de solicitud aprobada: {enviados} enviados, {errores} errores")
        
        return {
            'success': True,
            'task_id': task_id,
            'total_destinatarios': len(destinatarios),
            'enviados': enviados,
            'errores': errores,
            'resultados': resultados,
            'solicitud_codigo': datos_aprobacion.get('codigo'),
            'tipo': 'solicitud_aprobada',
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        error_msg = f"Error en envío de solicitud aprobada: {str(e)}"
        logger.error(f"[{task_id}] ❌ {error_msg}")
        return {
            'success': False,
            'task_id': task_id,
            'error': error_msg,
            'tipo': 'solicitud_aprobada'
        }