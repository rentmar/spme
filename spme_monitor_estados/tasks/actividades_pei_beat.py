# tasks/actividades_pei_beat.py
# Propósito: Tarea Beat para verificar actividades PEI
# Se ejecuta según configuración en admin (recomendado: cada 12h)

from celery import shared_task
import logging

from spme_monitor_estados.models.configuracion import ConfiguracionMonitoreo
from spme_monitor_estados.services.verificadores.actividad_pei_verificador import procesar_actividades_pei

logger = logging.getLogger(__name__)

@shared_task(
    name='monitor.actividades_pei_beat',
    rate_limit='2/m',
    bind=True
)
def verificar_actividades_pei_beat(self):
    """
    TAREA BEAT: Verificar Actividades PEI
    Frecuencia recomendada: Cada 12 horas
    Cola: correo
    
    Verifica actividades PEI y aplica cambios automáticos:
    - PLAN → EJEC: cuando tiene indicadores asociados
    - EJEC → RETR → REPROG: cuando fecha cierre < hoy
    - EJEC/RETR → REP: cuando tiene informe PEI
    
    Returns:
        dict: Resultados de la verificación
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] " + "="*60)
    logger.info(f"[{task_id}] 🚀 VERIFICANDO ACTIVIDADES PEI")
    logger.info(f"[{task_id}] " + "="*60)
    
    try:
        # Obtener configuración para actividades PEI
        config = ConfiguracionMonitoreo.objects.get(
            tipo_entidad='actividad_pei',
            activo=True
        )
        
        logger.info(f"[{task_id}] 📋 Configuración: {config}")
        
        # Procesar todas las actividades PEI
        resultado = procesar_actividades_pei(config)
        
        logger.info(f"[{task_id}] ✅ Actividades PEI procesadas: {resultado.get('procesadas', 0)}")
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
        logger.error(f"[{task_id}] ❌ Configuración de actividades PEI no encontrada")
        return {'error': 'Configuración no encontrada'}
    except Exception as e:
        logger.error(f"[{task_id}] ❌ Error en verificación de actividades PEI: {e}")
        return {'error': str(e)}