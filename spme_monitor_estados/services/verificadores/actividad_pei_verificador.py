# services/verificadores/actividad_pei_verificador.py
# Propósito: Verificador específico para Actividades PEI
# Aplica criterios específicos para actividades del PEI

from ..base.verificador_base import VerificadorBase
from spme_actividades.models import ActividadPei
from spme_monitoreo.models import InformeActividadPrincipalPei
from ..notificadores.notificador_mensajes import NotificadorMensajes
from ..notificadores.notificador_email_lotes import NotificadorEmailLotes
from ..historial.historial_service import HistorialService
import logging

logger = logging.getLogger(__name__)

class ActividadPeiVerificador(VerificadorBase):
    """
    Verificador para Actividades PEI
    CRITERIOS:
    - PLAN → EJEC: Tiene indicadores asociados
    - EJEC → RETR: Fecha cierre < hoy
    - RETR → REPROG: Automático
    - EJEC/RETR → REP: Tiene informe PEI
    """
    
    def obtener_queryset(self):
        """
        Obtiene actividades PEI activas en estados relevantes.
        """
        return ActividadPei.objects.filter(
            estaInactiva=False,
            estado__in=['PLAN', 'EJEC', 'RETR']
        ).select_related('responsable').prefetch_related(
            'indicadores_cuantitativos',
            'indicadores_cualitativos'
        )
    
    def verificar_entidad(self, actividad):
        """
        Verifica una actividad PEI individual.
        
        Args:
            actividad: La actividad PEI a verificar
            
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
        # CASO 1: PLAN → EJEC (tiene indicadores)
        # ============================================================
        if actividad.estado == 'PLAN' and self._tiene_indicadores(actividad):
            resultado = self._cambiar_a_ejec(actividad)
            resultados['cambio_realizado'] = True
            resultados['cambio'] = resultado
            
            # REGISTRAR HISTORIAL
            HistorialService.registrar_cambio(
                tipo_entidad='actividad_pei',
                entidad=actividad,
                cambio_info={
                    'estado_anterior': 'PLAN',
                    'estado_nuevo': 'EJEC',
                    'motivo': 'Inicio por tener indicadores',
                    'automatico': True
                }
            )
            
            notif = notificador_mensajes.notificar('actividad_pei', 'inicio', actividad, {})
            resultados['notificaciones'] += 1 if notif else 0
            
            email = notificador_email.notificar('actividad_pei', 'inicio', actividad, {})
            resultados['emails_encolados'] += 1 if email else 0
        
        # ============================================================
        # CASO 2: EJEC → RETR (fecha pasada)
        # ============================================================
        elif actividad.estado == 'EJEC' and self._esta_retrasada(actividad):
            dias = self._dias_retraso(actividad)
            
            # RETR
            self._cambiar_a_retr(actividad, dias)
            # REPROG (automático)
            resultado = self._cambiar_a_reprog(actividad)
            
            resultados['cambio_realizado'] = True
            resultados['cambio'] = resultado
            
            # REGISTRAR HISTORIAL
            HistorialService.registrar_cambio(
                tipo_entidad='actividad_pei',
                entidad=actividad,
                cambio_info={
                    'estado_anterior': 'EJEC',
                    'estado_nuevo': 'REPROG',
                    'motivo': f'Retraso de {dias} días',
                    'automatico': True,
                    'detalles': {'dias': dias}
                }
            )
            
            evento = 'retraso_critico' if dias >= 15 else 'retraso'
            notif = notificador_mensajes.notificar('actividad_pei', evento, actividad, {'dias': dias})
            resultados['notificaciones'] += 1 if notif else 0
            
            email = notificador_email.notificar('actividad_pei', evento, actividad, {'dias': dias})
            resultados['emails_encolados'] += 1 if email else 0
        
        # ============================================================
        # CASO 3: EJEC/RETR → REP (tiene informe)
        # ============================================================
        elif actividad.estado in ['EJEC', 'RETR'] and self._tiene_informe(actividad):
            resultado = self._cambiar_a_rep(actividad)
            resultados['cambio_realizado'] = True
            resultados['cambio'] = resultado
            
            # REGISTRAR HISTORIAL
            HistorialService.registrar_cambio(
                tipo_entidad='actividad_pei',
                entidad=actividad,
                cambio_info={
                    'estado_anterior': actividad.estado,
                    'estado_nuevo': 'REP',
                    'motivo': 'Paso a reporte por tener informe',
                    'automatico': True
                }
            )
            
            notif = notificador_mensajes.notificar('actividad_pei', 'reporte', actividad, {})
            resultados['notificaciones'] += 1 if notif else 0
            
            email = notificador_email.notificar('actividad_pei', 'reporte', actividad, {})
            resultados['emails_encolados'] += 1 if email else 0
        
        return resultados
    
    def _tiene_indicadores(self, actividad):
        """
        Verifica si la actividad PEI tiene indicadores asociados.
        """
        return (actividad.indicadores_cuantitativos.exists() or 
                actividad.indicadores_cualitativos.exists())
    
    def _esta_retrasada(self, actividad):
        """
        Verifica si la fecha de cierre ya pasó.
        """
        if not actividad.fecha_cierre:
            return False
        return self.hoy > actividad.fecha_cierre
    
    def _dias_retraso(self, actividad):
        """
        Calcula días de retraso.
        """
        if not actividad.fecha_cierre:
            return 0
        return (self.hoy - actividad.fecha_cierre).days
    
    def _tiene_informe(self, actividad):
        """
        Verifica si tiene informe PEI.
        """
        return InformeActividadPrincipalPei.objects.filter(actividad=actividad).exists()
    
    def _cambiar_a_ejec(self, actividad):
        """
        Cambia PLAN → EJEC.
        """
        estado_anterior = actividad.estado
        actividad.estado = 'EJEC'
        if not actividad.fecha_inicio:
            actividad.fecha_inicio = self.hoy
        actividad.gradoEjecucion = '0%'
        actividad.save()
        
        logger.info(f"✅ Actividad PEI {actividad.codigo}: {estado_anterior} → EJEC")
        return {
            'estado_anterior': estado_anterior,
            'estado_nuevo': 'EJEC',
            'motivo': 'Inicio por tener indicadores'
        }
    
    def _cambiar_a_retr(self, actividad, dias):
        """
        Cambia a RETR (solo estado, sin retorno).
        """
        actividad.estado = 'RETR'
        actividad.gradoEjecucion = f"Retraso: {dias} días"
        actividad.save()
        logger.warning(f"⚠️ Actividad PEI {actividad.codigo}: → RETR ({dias} días)")
    
    def _cambiar_a_reprog(self, actividad):
        """
        Cambia RETR → REPROG.
        """
        estado_anterior = actividad.estado
        actividad.estado = 'REPROG'
        actividad.gradoEjecucion = 'Requiere reprogramación'
        actividad.save()
        
        logger.info(f"📅 Actividad PEI {actividad.codigo}: → REPROG")
        return {
            'estado_anterior': estado_anterior,
            'estado_nuevo': 'REPROG',
            'motivo': 'Requiere reprogramación por retraso'
        }
    
    def _cambiar_a_rep(self, actividad):
        """
        Cambia a REP (en reporte).
        """
        estado_anterior = actividad.estado
        actividad.estado = 'REP'
        actividad.gradoEjecucion = 'En reporte'
        actividad.save()
        
        logger.info(f"📋 Actividad PEI {actividad.codigo}: {estado_anterior} → REP")
        return {
            'estado_anterior': estado_anterior,
            'estado_nuevo': 'REP',
            'motivo': 'Paso a reporte por tener informe'
        }


def procesar_actividades_pei(config):
    """
    Función de entrada para la tarea Beat.
    
    Args:
        config: ConfiguracionMonitoreo para actividades PEI
        
    Returns:
        dict: Resultados del procesamiento
    """
    verificador = ActividadPeiVerificador(config)
    return verificador.procesar_todas()