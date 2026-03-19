# tasks/actividades_beat.py
# Propósito: Tarea Beat para verificar actividades
# Se ejecuta según configuración en admin (recomendado: cada 6h)

from celery import shared_task
import logging

from spme_monitor_estados.models.configuracion import ConfiguracionMonitoreo
from spme_monitor_estados.services.verificadores.actividad_verificador import procesar_actividades

logger = logging.getLogger(__name__)

@shared_task(
    name='monitor.actividades_beat',
    rate_limit='2/m',  # Máximo 2 ejecuciones por minuto (protección)
    bind=True
)
def verificar_actividades_beat(self):
    """
    TAREA BEAT: Verificar Actividades
    Frecuencia recomendada: Cada 6 horas
    Cola: correo
    
    Esta tarea es disparada por Celery Beat según la configuración en admin.
    Verifica actividades en estado EJEC y aplica cambios automáticos:
    - EJEC → RETR → REPROG (cuando está fuera de fecha y sin formularios)
    - EJEC → REP (cuando tiene informe de actividad)
    
    Returns:
        dict: Resultados de la verificación
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] " + "="*60)
    logger.info(f"[{task_id}] 🚀 VERIFICANDO ACTIVIDADES")
    logger.info(f"[{task_id}] " + "="*60)
    
    try:
        # Obtener configuración para actividades
        config = ConfiguracionMonitoreo.objects.get(
            tipo_entidad='actividad',
            activo=True
        )
        
        logger.info(f"[{task_id}] 📋 Configuración: {config}")
        
        # Procesar todas las actividades
        resultado = procesar_actividades(config)
        
        # Logging de resultados
        logger.info(f"[{task_id}] ✅ Actividades procesadas: {resultado.get('procesadas', 0)}")
        logger.info(f"[{task_id}] ✅ Cambios realizados: {resultado.get('cambios', 0)}")
        logger.info(f"[{task_id}] ✅ Notificaciones internas: {resultado.get('notificaciones', 0)}")
        logger.info(f"[{task_id}] ✅ Emails encolados: {resultado.get('emails_encolados', 0)}")
        
        if resultado.get('detalles'):
            logger.info(f"[{task_id}] 📝 Detalles de cambios:")
            for detalle in resultado['detalles']:
                cambio = detalle.get('cambio', {})
                logger.info(f"[{task_id}]   • {detalle.get('codigo')}: {cambio.get('estado_anterior')} → {cambio.get('estado_nuevo')}")
        
        return resultado
        
    except ConfiguracionMonitoreo.DoesNotExist:
        logger.error(f"[{task_id}] ❌ Configuración de actividades no encontrada o inactiva")
        return {'error': 'Configuración no encontrada'}
    except Exception as e:
        logger.error(f"[{task_id}] ❌ Error en verificación de actividades: {e}")
        return {'error': str(e)}