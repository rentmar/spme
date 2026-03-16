# services/verificadores/tarea_verificador.py
# Propósito: Verificador específico para Tareas de Actividad
# Detecta tareas vencidas y las completa automáticamente

from ..base.verificador_base import VerificadorBase
from spme_actividades.models import TareaActividad
from ..notificadores.notificador_mensajes import NotificadorMensajes
from ..notificadores.notificador_email_lotes import NotificadorEmailLotes
from ..historial.historial_service import HistorialService
import logging

logger = logging.getLogger(__name__)

class TareaVerificador(VerificadorBase):
    """
    Verificador para Tareas de Actividad
    CRITERIOS:
    - COMPL: Fecha límite < hoy (vencida automáticamente)
    """
    
    def obtener_queryset(self):
        """
        Obtiene las tareas pendientes o en progreso que tienen fecha límite.
        """
        return TareaActividad.objects.filter(
            estado__in=['PEN', 'EPROG'],
            fecha_limite__isnull=False
        ).select_related('actividad__responsable')
    
    def verificar_entidad(self, tarea):
        """
        Verifica una tarea individual.
        
        Args:
            tarea: La tarea a verificar
            
        Returns:
            dict: Resultado de la verificación
        """
        resultados = {
            'cambio_realizado': False,
            'cambio': None,
            'notificaciones': 0,
            'emails_encolados': 0
        }
        
        notificador_mensajes = NotificadorMensajes(self.config)
        notificador_email = NotificadorEmailLotes(self.config)
        
        # ============================================================
        # CASO: Tarea vencida (fecha límite pasada)
        # ============================================================
        if self.hoy > tarea.fecha_limite:
            dias = (self.hoy - tarea.fecha_limite).days
            
            # Cambiar estado a COMPL
            estado_anterior = tarea.estado
            tarea.estado = 'COMPL'
            tarea.save()
            
            resultados['cambio_realizado'] = True
            resultados['cambio'] = {
                'estado_anterior': estado_anterior,
                'estado_nuevo': 'COMPL',
                'motivo': f"Vencida por {dias} días"
            }
            
            # REGISTRAR HISTORIAL
            HistorialService.registrar_cambio(
                tipo_entidad='tarea',
                entidad=tarea,
                cambio_info={
                    'estado_anterior': estado_anterior,
                    'estado_nuevo': 'COMPL',
                    'motivo': f"Vencida por {dias} días",
                    'automatico': True,
                    'detalles': {'dias': dias}
                }
            )
            
            # Notificaciones
            notif = notificador_mensajes.notificar('tarea', 'vencida', tarea, {'dias': dias})
            resultados['notificaciones'] += 1 if notif else 0
            
            email = notificador_email.notificar('tarea', 'vencida', tarea, {'dias': dias})
            resultados['emails_encolados'] += 1 if email else 0
            
            logger.info(f"✅ Tarea {tarea.codigo}: {estado_anterior} → COMPL (vencida {dias} días)")
        
        return resultados


def procesar_tareas(config):
    """
    Función de entrada para la tarea Beat.
    
    Args:
        config: ConfiguracionMonitoreo para tareas
        
    Returns:
        dict: Resultados del procesamiento
    """
    verificador = TareaVerificador(config)
    return verificador.procesar_todas()