from celery import shared_task
from django.core.mail  import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60, time_limit=30, queue='correo', )
def send_templated_email(self, to_email, template_name, context, subject=None):
    """
    Envía email con plantilla de forma asíncrona

    Args:
        to_email: Destinatario
        template_name: Nombre del template (welcome, notification, report)
        context: Diccionario con datos para el template
        subject: Asunto del email (opcional)
    """
    logger.info(f"📧 Enviando email a {to_email} - Template: {template_name}")

    # Agregar current_year que necesita base.html
    context['current_year'] = datetime.now().year

    # Asuntos por defecto
    default_subjects = {
        'welcome': '¡Bienvenido a SPME!',
        'notification': context.get('notification_title', 'Notificación SPME'),
        'report': context.get('report_title', 'Reporte SPME'),
    }

    if not subject:
        subject = default_subjects.get(template_name, 'Mensaje SPME')

    try:
        # Renderizar plantilla
        html_content = render_to_string(f'email/{template_name}.html', context)

        # Texto plano
        text_content = f"Hola {context.get('user_name', 'Usuario')}, tienes un mensaje de SPME."
        
        # Enviar email
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )

        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        logger.info(f"✅ Email enviado a {to_email}")

        return {
            'status': 'success',
            'to_email': to_email,
            'template': template_name,
        }

    except Exception as exc:
        logger.error(f"❌ Error enviando a {to_email}: {str(exc)}")
        countdown = 60 * (2 ** self.request.retries)


@shared_task(bind=True, max_retries=3, default_retry_delay=60, time_limit=30, queue='correo')
def send_notificacion_email(self, subject, template_name, context, to_emails):
    """
    Envía email de notificación de forma asíncrona vía Celery + RabbitMQ.
    
    Args:
        subject: Asunto del correo
        template_name: Ruta completa del template (ej: correos/sistema/...)
        context: Diccionario con datos para el template
        to_emails: Lista de destinatarios
    """

    logger.info(f"📧 Enviando: {subject} -> {to_emails}")
    context.setdefault('current_year', datetime.now().year)
    try:
        html_content = render_to_string(template_name, context)
        text_content = _strip_html(html_content)
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to_emails,
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"✅ Enviado: {subject}")
        return {'status': 'success', 'to_emails': to_emails, 'subject': subject}

    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        raise self.retry(exc=e)


def _strip_html(html: str) -> str:
    """Convierte HTML a texto plano para el cuerpo alternativo."""
    text = re.sub(r'<[^>]+>', '', html)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()