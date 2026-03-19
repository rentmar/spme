# tasks/email_lotes_beat.py
# Propósito: Tarea Beat que procesa los emails encolados
# Se ejecuta cada 5 minutos y envía lotes de 25 emails

from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
import logging

from spme_monitor_estados.models.cola_email import EmailEnCola

logger = logging.getLogger(__name__)

@shared_task(
    name='monitor.procesar_lotes_email_beat',
    rate_limit='10/m',  # Máximo 10 lotes por minuto
    bind=True
)
def procesar_lotes_email_beat(self):
    """
    TAREA BEAT: Procesar lotes de emails pendientes
    Frecuencia recomendada: Cada 5 minutos
    Cola: correo
    
    Toma emails de la tabla EmailEnCola y los envía en lotes,
    priorizando los de mayor prioridad.
    
    Características:
    - Procesa por prioridad (4→3→2→1)
    - Máximo 25 emails por lote
    - Reintenta emails fallidos hasta 3 veces
    - Actualiza estado en BD
    
    Returns:
        dict: Estadísticas del procesamiento
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] " + "="*60)
    logger.info(f"[{task_id}] 📧 PROCESANDO LOTE DE EMAILS")
    logger.info(f"[{task_id}] " + "="*60)
    
    resultados = {
        'procesados': 0,
        'exitosos': 0,
        'fallidos': 0,
        'pendientes': 0,
        'detalles': []
    }
    
    # ============================================================
    # Procesar por prioridad (primero los más altos)
    # ============================================================
    for prioridad in [4, 3, 2, 1]:
        # Obtener lote de emails de esta prioridad
        lote = EmailEnCola.obtener_lote(
            limite=25,  # Máximo 25 por lote para no saturar
            prioridad_minima=prioridad
        )
        
        if not lote:
            continue
        
        logger.info(f"[{task_id}] 📊 Lote prioridad {prioridad}: {len(lote)} emails")
        
        # Procesar cada email del lote
        for email in lote:
            resultados['procesados'] += 1
            exito, detalle = _enviar_email(email, task_id)
            
            if exito:
                resultados['exitosos'] += 1
                resultados['detalles'].append({
                    'id': email.id,
                    'destinatario': email.destinatario,
                    'asunto': email.asunto,
                    'resultado': 'exitoso'
                })
            else:
                resultados['fallidos'] += 1
                resultados['detalles'].append({
                    'id': email.id,
                    'destinatario': email.destinatario,
                    'asunto': email.asunto,
                    'resultado': 'fallido',
                    'error': detalle
                })
    
    # Contar cuántos quedan pendientes
    resultados['pendientes'] = EmailEnCola.objects.filter(
        estado='pendiente'
    ).count()
    
    # Logging de resultados
    logger.info(f"[{task_id}] ✅ Procesados: {resultados['procesados']}")
    logger.info(f"[{task_id}] ✅ Exitosos: {resultados['exitosos']}")
    logger.info(f"[{task_id}] ❌ Fallidos: {resultados['fallidos']}")
    logger.info(f"[{task_id}] ⏳ Pendientes: {resultados['pendientes']}")
    
    return resultados


def _enviar_email(email, task_id):
    """
    Función interna para enviar un email individual
    
    Args:
        email: Objeto EmailEnCola a enviar
        task_id: ID de la tarea para logging
    
    Returns:
        tuple: (bool éxito, str detalle)
    """
    try:
        # Crear mensaje
        msg = EmailMultiAlternatives(
            subject=email.asunto,
            body=email.cuerpo_texto,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email.destinatario],
            cc=email.copia,
            bcc=email.copia_oculta,
        )
        
        # Adjuntar versión HTML
        msg.attach_alternative(email.cuerpo_html, "text/html")
        
        # Enviar (aquí se conecta al servidor SMTP)
        msg.send(fail_silently=False)
        
        # Marcar como enviado en BD
        email.marcar_enviado()
        
        logger.info(f"[{task_id}] ✅ Email enviado: {email.asunto} a {email.destinatario}")
        return True, "OK"
        
    except Exception as e:
        # Marcar error y programar reintento si corresponde
        error_msg = str(e)
        email.marcar_error(error_msg)
        
        logger.error(f"[{task_id}] ❌ Error enviando email {email.id}: {error_msg}")
        return False, error_msg