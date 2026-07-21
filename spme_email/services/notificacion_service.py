# spme/spme_email/services/notificacion_service.py
"""
Servicio de notificaciones. Reutilizable desde cualquier aplicación.

USO:
    from spme_email.services.notificacion_service import NotificacionService
    
    service = NotificacionService()
    service.enviar(
        tipo='fondos',
        solicitud_id=42,
        accion='revision',
        destinatarios_ids=[68, 71],
        base_url='https://spme.gob.bo',
    )
"""

from typing import List
from datetime import datetime
from django.conf import settings
import logging

#Servicio
from spme_email.services.base import BaseEmailService, EmailConfig
#Repositorio
from ..repositories.solicitud_repository import SolicitudRepository

logger = logging.getLogger(__name__)

TEMPLATE_MAP = {
    'fondos': {'base_path': 'correos/sistema/formularios/solicitudFondos', 'repo_method': 'get_solicitud_fondos'},
    'reposicion': {'base_path': 'correos/sistema/formularios/solicitudReembolso', 'repo_method': 'get_solicitud_reembolso'},
    'viaje': {'base_path': 'correos/sistema/formularios/solicitudViaje', 'repo_method': 'get_solicitud_viaje'},
    'pago_directo': {'base_path': 'correos/sistema/formularios/solicitudPagoDirecto', 'repo_method': 'get_solicitud_pago_directo'},
    'rendicion': {'base_path': 'correos/sistema/formularios/rendicionCuentas', 'repo_method': 'get_rendicion_cuentas'},
}

ACCION_MAP = {
    'revision': {'template': 'peticion_revision.html', 'subject': 'Revisión {tipo} - {codigo}'},
    'aprobacion': {'template': 'aprobacion.html', 'subject': '{tipo} Aprobada - {codigo}'},
    'rechazo': {'template': 'rechazo.html', 'subject': '{tipo} Rechazada - {codigo}'},
    'nueva_revision': {'template': 'nueva_revision.html', 'subject': 'Nueva Revisión {tipo} - {codigo}'},
}

TIPO_NOMBRE_MAP = {
    'fondos': 'Solicitud de Fondos',
    'reposicion': 'Solicitud de Reposición',
    'viaje': 'Solicitud de Viaje',
    'pago_directo': 'Pago Directo',
    'rendicion': 'Rendición de Cuentas',
}

class NotificacionService:

    def __init__(self):
        self.email_service = BaseEmailService()
        self.repository = SolicitudRepository()

    def enviar(self, tipo, solicitud_id, accion, destinatarios_ids, base_url=''):
        """
        Envía una notificación.
        Args:
            tipo: 'fondos'|'reposicion'|'viaje'|'pago_directo'|'rendicion'
            solicitud_id: ID de la solicitud
            accion: 'revision'|'aprobacion'|'rechazo'|'nueva_revision'
            destinatarios_ids: Lista de IDs de usuarios
            base_url: URL base del frontend
        
        Returns:
            dict: {'task_id', 'to_emails', 'subject'}
        """
        #Comprobar si el tipo de formulario existe
        if tipo not in TEMPLATE_MAP:
            raise ValueError(f"Tipo no soportado: {tipo}")
        #Combrobar si existe la accion
        if accion not in ACCION_MAP:
            raise ValueError(f"Acción no soportada: {accion}")
        
        #definir el tipo y la accion
        tipo_config = TEMPLATE_MAP[tipo]
        accion_config = ACCION_MAP[accion]
        # print('************* Tipo y Accion *****************************')
        # print('tipo: ', tipo_config)
        # print('Accion: ', accion_config)
        # print('********************************************************')

        #Contexto desde el modelo
        solicitud = self._get_solicitud(tipo, solicitud_id)
        context = solicitud.get_mensaje_contexto()
        # print('************* Solicitud y Contexto *****************************')
        # print('Solicitud: ', solicitud)
        # print('contexto: ', context)
        # print('******************************************************')

        #Construir la URL y colocarla en el contexto
        if 'accion_url' in context:
            context['accion_url'] = self._build_absolute_url(context['accion_url'], base_url)
        
        context.setdefault('current_year', datetime.now().year)

        # print('************* URL y ajuste de contexto *****************************')
        # print('CONTEXTO AJUSTADO: ', context)
        # print('******************************************')

        #Obtener los emails de los destinatarios
        destinatarios = self.repository.get_usuarios_por_ids(destinatarios_ids)
        to_emails = [d['email'] for d in destinatarios if d['email']]
        if not to_emails:
            raise ValueError("No se encontraron emails para los destinatarios")
        # print('************* Emails de los destinatarios *****************************')
        # print('emails: ', to_emails)
        # print('*************************************************************************')

        #Template y el asunto
        template_path = f"{tipo_config['base_path']}/{accion_config['template']}"
        subject = accion_config['subject'].format(
            tipo=TIPO_NOMBRE_MAP[tipo],
            codigo=context.get('codigo', ''),
        )
        # print('************* Ruta del Template y Asunto *****************************')
        # print('template ruta: ', template_path)
        # print('Asunto email:', subject)
        # print('************************************************************')

        #Enviar

        config = EmailConfig(subject=subject, template_name=template_path, context=context, to_emails=to_emails)
        task_id = self.email_service.send_async(config)
        logger.info(f"Notificación {accion}: {subject} -> {to_emails}")
        return {'task_id': task_id, 'to_emails': to_emails, 'subject': subject}


    #Devuelve la solicitud
    def _get_solicitud(self, tipo, solicitud_id):
        config = TEMPLATE_MAP.get(tipo)
        if not config:
            raise ValueError(f"Tipo no soportado: {tipo}")
        return getattr(self.repository, config['repo_method'])(solicitud_id)
    
    #Funcion para construir el email
    def _build_absolute_url(self, relative_url, base_url=''):
        if not base_url:
            base_url = getattr(settings, 'APP_URL', 'http://localhost:5173')
        return f"{base_url.rstrip('/')}/{relative_url.lstrip('/')}"