# spme/spme_email/services/base.py
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging


logger = logging.getLogger(__name__)

@dataclass
class EmailConfig:
    """
    Configuracion para cualquier email de sistema
    """
    subject: str
    template_name: str
    context: Dict[str, Any]
    to_emails: List[str]
    cc_emails: Optional[List[str]] = field(default_factory=list)
    bcc_emails: Optional[List[str]] = field(default_factory=list)
    from_email: Optional[str] = None


class BaseEmailService:
    """
    Servicio Base para envio de Emails Asincronos via celery
    """
    def send_async(self, config: EmailConfig) -> str:
        """
        Encola un email para envío asíncrono.
        
        Args:
            config: EmailConfig con subject, template_name, context, to_emails
            
        Returns:
            str: task_id de Celery
        """
        from spme_email.tasks.email_tasks import send_notificacion_email

        task = send_notificacion_email.delay(
            subject=config.subject,
            template_name=config.template_name,
            context=config.context,
            to_emails=config.to_emails,
        )
        logger.info(f"Encolado: {task.id} - {config.subject}")
        return task.id
