# tasks/tareas_pei_beat.py
# Propósito: Tarea Beat para verificar tareas PEI
# Se ejecuta según configuración en admin (recomendado: cada 2h)

from celery import shared_task
import logging

from spme_monitor_estados.models.configuracion import ConfiguracionMonitoreo
from spme_monitor_estados.services.verificadores.tarea_pei_verificador import procesar_tareas_pei

logger = logging.getLogger(__name__)

@shared_task(
    name='monitor.tareas_pei_beat',
    rate_limit='5/m',
    bind=True
)
def verificar_tareas_pei_beat(self):
    """
    TAREA BEAT: Verificar Tareas PEI
    Frecuencia recomendada: Cada 2 horas
    Cola: correo
    
    Verifica tareas PEI y las completa automáticamente cuando:
    - Fecha límite < hoy (vencida)
    - Tiene informe PEI asociado (solo si está en progreso)
    
    Returns:
        dict: Resultados de la verificación
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] " + "="*60)
    logger.info(f"[{task_id}] 🚀 VERIFICANDO TAREAS PEI")
    logger.info(f"[{task_id}] " + "="*60)
    
    try:
        # Obtener configuración para tareas PEI
        config = ConfiguracionMonitoreo.objects.get(
            tipo_entidad='tarea_pei',
            activo=True
        )
        
        logger.info(f"[{task_id}] 📋 Configuración: {config}")
        
        # Procesar todas las tareas PEI
        resultado = procesar_tareas_pei(config)
        
        logger.info(f"[{task_id}] ✅ Tareas PEI procesadas: {resultado.get('procesadas', 0)}")
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
        logger.error(f"[{task_id}] ❌ Configuración de tareas PEI no encontrada")
        return {'error': 'Configuración no encontrada'}
    except Exception as e:
        logger.error(f"[{task_id}] ❌ Error en verificación de tareas PEI: {e}")
        return {'error': str(e)}