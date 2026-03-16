# tasks/tareas_beat.py
# Propósito: Tarea Beat para verificar tareas
# Se ejecuta según configuración en admin (recomendado: cada 1h)

from celery import shared_task
import logging

from spme_monitor_estados.models.configuracion import ConfiguracionMonitoreo
from spme_monitor_estados.services.verificadores.tarea_verificador import procesar_tareas

logger = logging.getLogger(__name__)

@shared_task(
    name='monitor.tareas_beat',
    rate_limit='5/m',  # Máximo 5 ejecuciones por minuto
    bind=True
)
def verificar_tareas_beat(self):
    """
    TAREA BEAT: Verificar Tareas de Actividad
    Frecuencia recomendada: Cada 1 hora
    Cola: correo
    
    Detecta tareas vencidas y las completa automáticamente.
    Una tarea se considera vencida cuando su fecha_limite es menor a hoy.
    
    Returns:
        dict: Resultados de la verificación
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] " + "="*60)
    logger.info(f"[{task_id}] 🚀 VERIFICANDO TAREAS")
    logger.info(f"[{task_id}] " + "="*60)
    
    try:
        # Obtener configuración para tareas
        config = ConfiguracionMonitoreo.objects.get(
            tipo_entidad='tarea',
            activo=True
        )
        
        logger.info(f"[{task_id}] 📋 Configuración: {config}")
        
        # Procesar todas las tareas
        resultado = procesar_tareas(config)
        
        logger.info(f"[{task_id}] ✅ Tareas procesadas: {resultado.get('procesadas', 0)}")
        logger.info(f"[{task_id}] ✅ Cambios realizados: {resultado.get('cambios', 0)}")
        logger.info(f"[{task_id}] ✅ Notificaciones: {resultado.get('notificaciones', 0)}")
        logger.info(f"[{task_id}] ✅ Emails encolados: {resultado.get('emails_encolados', 0)}")
        
        if resultado.get('detalles'):
            logger.info(f"[{task_id}] 📝 Detalles de cambios:")
            for detalle in resultado['detalles']:
                cambio = detalle.get('cambio', {})
                logger.info(f"[{task_id}]   • {detalle.get('codigo')}: {cambio.get('estado_anterior')} → {cambio.get('estado_nuevo')}")
        
        return resultado
        
    except ConfiguracionMonitoreo.DoesNotExist:
        logger.error(f"[{task_id}] ❌ Configuración de tareas no encontrada")
        return {'error': 'Configuración no encontrada'}
    except Exception as e:
        logger.error(f"[{task_id}] ❌ Error en verificación de tareas: {e}")
        return {'error': str(e)}