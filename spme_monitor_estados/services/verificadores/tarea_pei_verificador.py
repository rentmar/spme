# services/verificadores/tarea_pei_verificador.py
# Propósito: Verificador específico para Tareas de Actividad PEI

from ..base.verificador_base import VerificadorBase
from spme_actividades.models import TareaActividadPei
from spme_monitoreo.models import InformeTareaPrincipalPei
from ..historial.historial_service import HistorialService
import logging

logger = logging.getLogger(__name__)

class TareaPeiVerificador(VerificadorBase):
    """
    Verificador para Tareas de Actividad PEI
    CRITERIOS:
    - COMPL: Fecha límite < hoy (vencida) o tiene informe
    """
    
    def obtener_queryset(self):
        """
        Obtiene tareas PEI pendientes o en progreso.
        """
        return TareaActividadPei.objects.filter(
            estado__in=['PEN', 'EPROG']
        ).select_related('actividad__responsable')
    
    def verificar_entidad(self, tarea):
        """
        Verifica una tarea PEI individual.
        
        Args:
            tarea: La tarea PEI a verificar
            
        Returns:
            dict: Resultado de la verificación
        """
        resultados = {
            'cambio_realizado': False,
            'cambio': None,
            'notificaciones': 0,
            'emails_encolados': 0
        }
        
        # ============================================================
        # CASO 1: Vencimiento
        # ============================================================
        if tarea.fecha_limite and self.hoy > tarea.fecha_limite:
            return self._completar_por_vencimiento(tarea)
        
        # ============================================================
        # CASO 2: Tiene informe (solo si está en progreso)
        # ============================================================
        if tarea.estado == 'EPROG' and self._tiene_informe(tarea):
            return self._completar_por_informe(tarea)
        
        return resultados
    
    def _tiene_informe(self, tarea):
        """
        Verifica si la tarea tiene informe asociado.
        """
        return InformeTareaPrincipalPei.objects.filter(tarea=tarea).exists()
    
    def _completar_por_vencimiento(self, tarea):
        """
        Completa la tarea por vencimiento.
        """
        dias = (self.hoy - tarea.fecha_limite).days
        estado_anterior = tarea.estado
        tarea.estado = 'COMPL'
        tarea.save()
        
        # REGISTRAR HISTORIAL
        HistorialService.registrar_cambio(
            tipo_entidad='tarea_pei',
            entidad=tarea,
            cambio_info={
                'estado_anterior': estado_anterior,
                'estado_nuevo': 'COMPL',
                'motivo': f"Vencida por {dias} días",
                'automatico': True,
                'detalles': {'dias': dias}
            }
        )
        
        logger.info(f"✅ Tarea PEI {tarea.codigo}: {estado_anterior} → COMPL (vencida {dias} días)")
        
        return {
            'cambio_realizado': True,
            'cambio': {
                'estado_anterior': estado_anterior,
                'estado_nuevo': 'COMPL',
                'motivo': f"Vencida por {dias} días"
            },
            'notificaciones': 0,
            'emails_encolados': 0
        }
    
    def _completar_por_informe(self, tarea):
        """
        Completa la tarea por tener informe.
        """
        estado_anterior = tarea.estado
        tarea.estado = 'COMPL'
        tarea.save()
        
        # REGISTRAR HISTORIAL
        HistorialService.registrar_cambio(
            tipo_entidad='tarea_pei',
            entidad=tarea,
            cambio_info={
                'estado_anterior': estado_anterior,
                'estado_nuevo': 'COMPL',
                'motivo': 'Completada por tener informe',
                'automatico': True
            }
        )
        
        logger.info(f"✅ Tarea PEI {tarea.codigo}: {estado_anterior} → COMPL (por informe)")
        
        return {
            'cambio_realizado': True,
            'cambio': {
                'estado_anterior': estado_anterior,
                'estado_nuevo': 'COMPL',
                'motivo': 'Completada por tener informe'
            },
            'notificaciones': 0,
            'emails_encolados': 0
        }


def procesar_tareas_pei(config):
    """
    Función de entrada para la tarea Beat.
    
    Args:
        config: ConfiguracionMonitoreo para tareas PEI
        
    Returns:
        dict: Resultados del procesamiento
    """
    verificador = TareaPeiVerificador(config)
    return verificador.procesar_todas()