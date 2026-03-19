# spme_mensajes/tasks/tareas_prueba.py

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone

@shared_task(name='correo.enviar_prueba_beat') 
def enviar_correo_prueba_beat():
    """Tarea periódica de prueba para Celery Beat"""
    
    # Enviar correo
    send_mail(
        subject='Prueba Celery Beat',
        message=f'Correo enviado a las {timezone.now()}',
        from_email='spmenotificaciones@gmail.com',
        recipient_list=['rolquezamarcelo@gmail.com'],
        fail_silently=False,
    )
    
    # Imprimir mensaje
    print("✅ Correo enviado por Beat")
    
    return "Correo enviado por Beat"


@shared_task(name='correo.tarea_beat_prueba')
def tarea_beat_prueba():
    """
    Tarea de prueba para Celery Beat
    Imprime TAREA BEAT cada 2 minutos
    """
    print("="*50)
    print("🎯 TAREA BEAT - EJECUTADA")
    print("="*50)
    
    return "TAREA BEAT completada"    