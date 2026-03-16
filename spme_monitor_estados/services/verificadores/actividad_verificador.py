# services/verificadores/actividad_verificador.py
# VERSIÓN 1.3: Extrae actividades en CRD, PLAN y RETR
# NOTA: Para PLAN se usa fecha_inicio (NO fecha_programada)

from ..base.verificador_base import VerificadorBase
from spme_actividades.models import Actividad
from django.db import models
import logging

logger = logging.getLogger(__name__)

class ActividadVerificador(VerificadorBase):
    """
    Verificador para Actividades - VERSIÓN 1.3
    Lista actividades y extrae las que están en CRD, PLAN y RETR
    """
    
    def obtener_queryset(self):
        """
        Obtiene todas las actividades activas.
        """
        queryset = Actividad.objects.filter(
            estaInactiva=False
        ).select_related('responsable')
        
        # Estadísticas por estado
        total = queryset.count()
        por_estado = queryset.values('estado').annotate(total=models.Count('id'))
        
        logger.info("="*60)
        logger.info(f"📊 ACTIVIDADES ENCONTRADAS: {total} total")
        for item in por_estado:
            logger.info(f"   • {item['estado']}: {item['total']}")
        logger.info("="*60)
        
        return queryset
    
    def verificar_entidad(self, actividad):
        """
        Lista actividades y extrae las que están en CRD, PLAN y RETR
        """
        # Siempre listamos la actividad
        logger.info(f"🔍 Actividad: {actividad.codigo}")
        logger.info(f"   • Nombre: {actividad.nombreCorto}")
        logger.info(f"   • Estado: {actividad.estado}")
        logger.info(f"   • Responsable: {actividad.responsable}")
        logger.info(f"   • Fecha inicio: {actividad.fecha_inicio}")  # ← NOTA: Para PLAN se usa fecha_inicio
        logger.info(f"   • Fecha cierre: {actividad.fecha_cierre}")
        logger.info(f"   • Grado ejecución: {actividad.gradoEjecucion}")
        
        # ============================================================
        # EXTRAER ACTIVIDADES EN CRD
        # ============================================================
        if actividad.estado == 'CRD':
            logger.info("   🟢 ACTIVIDAD EN CRD DETECTADA")
            logger.info(f"   • Estado: Creada - Pendiente de planificación")
        
        # ============================================================
        # EXTRAER ACTIVIDADES EN PLAN (USA fecha_inicio)
        # ============================================================
        elif actividad.estado == 'PLAN':
            logger.info("   🔵 ACTIVIDAD EN PLAN DETECTADA")
            logger.info(f"   • Estado: Planificada - Lista para ejecución")
            
            # Calcular días para inicio usando fecha_inicio
            if actividad.fecha_inicio:
                dias_para_inicio = (actividad.fecha_inicio - self.hoy).days
                
                if dias_para_inicio > 0:
                    logger.info(f"   • Inicia en: {dias_para_inicio} días")
                elif dias_para_inicio == 0:
                    logger.info(f"   • ¡INICIA HOY!")
                else:
                    logger.info(f"   • Debió iniciar hace {abs(dias_para_inicio)} días")
            else:
                logger.info(f"   • Sin fecha de inicio programada")
        
        # ============================================================
        # EXTRAER ACTIVIDADES EN RETRASO
        # ============================================================
        elif actividad.estado == 'RETR':
            logger.info("   🔴 ACTIVIDAD EN RETRASO DETECTADA")
            
            # Calcular días de retraso si hay fecha de cierre
            if actividad.fecha_cierre:
                dias_retraso = (self.hoy - actividad.fecha_cierre).days
                logger.info(f"   • Días de retraso: {dias_retraso}")
            else:
                logger.info(f"   • Sin fecha de cierre")
        
        logger.info("-" * 40)
        
        return {
            'cambio_realizado': False,
            'cambio': None,
            'notificaciones': 0,
            'emails_encolados': 0,
            'alertas': 0
        }
    
    def _obtener_crd(self):
        """
        Método auxiliar para obtener solo actividades en CRD
        """
        return Actividad.objects.filter(
            estaInactiva=False,
            estado='CRD'
        ).select_related('responsable')
    
    def _obtener_plan(self):
        """
        Método auxiliar para obtener solo actividades en PLAN
        """
        return Actividad.objects.filter(
            estaInactiva=False,
            estado='PLAN'
        ).select_related('responsable')
    
    def _obtener_retraso(self):
        """
        Metodo Auxiliar para obtener solo actividades en retraso
        """
        return Actividad.objects.filter(
            estaInactiva=False,
            estado='RETR',
        )


def procesar_actividades(config):
    """
    Función de entrada para la tarea Beat
    """
    logger.info("="*60)
    logger.info("🔍 INICIANDO LISTADO DE ACTIVIDADES (VERSIÓN 1.3 - CRD + PLAN + RETR)")
    logger.info("="*60)
    
    # Crear verificador
    verificador = ActividadVerificador(config)
    
    # ============================================================
    # EXTRAER ACTIVIDADES EN CRD
    # ============================================================
    actividades_crd = verificador._obtener_crd()
    total_crd = actividades_crd.count()
    
    logger.info(f"📌 ACTIVIDADES EN CRD: {total_crd}")
    if total_crd > 0:
        for act in actividades_crd:
            logger.info(f"   • {act.id} - {act.codigo} - {act.nombreCorto}")
    else:
        logger.info("   No hay actividades en estado CRD")
    
    # ============================================================
    # EXTRAER ACTIVIDADES EN PLAN (USA fecha_inicio)
    # ============================================================
    actividades_plan = verificador._obtener_plan()
    total_plan = actividades_plan.count()
    
    logger.info(f"📌 ACTIVIDADES EN PLAN: {total_plan}")
    if total_plan > 0:
        for act in actividades_plan:
            # Usar fecha_inicio (NO fecha_programada)
            if act.fecha_inicio:
                dias = (act.fecha_inicio - verificador.hoy).days
                if dias > 0:
                    estado_inicio = f"(inicia en {dias} días)"
                elif dias == 0:
                    estado_inicio = f"(INICIA HOY)"
                else:
                    estado_inicio = f"(RETRASADA {abs(dias)} días)"
                logger.info(f"   • {act.id} - {act.codigo} - {act.nombreCorto} {estado_inicio}")
            else:
                logger.info(f"   • {act.id} - {act.codigo} - {act.nombreCorto} (sin fecha de inicio)")
    else:
        logger.info("   No hay actividades en estado PLAN")
    
    # ============================================================
    # EXTRAER ACTIVIDADES EN RETRASO
    # ============================================================
    actividades_retr = verificador._obtener_retraso()
    total_retr = actividades_retr.count()
    
    logger.info(f"📌 ACTIVIDADES EN RETRASO: {total_retr}")
    if total_retr > 0:
        for act in actividades_retr:
            if act.fecha_cierre:
                dias = (verificador.hoy - act.fecha_cierre).days
                logger.info(f"   • {act.id} - {act.codigo} - {act.nombreCorto} (retraso: {dias} días)")
            else:
                logger.info(f"   • {act.id} - {act.codigo} - {act.nombreCorto}")
    else:
        logger.info("   No hay actividades en estado RETRASO")
    
    logger.info("="*60)
    
    # Procesar todas las actividades (las listará una por una)
    resultados = verificador.procesar_todas()
    
    return {
        'procesadas': resultados.get('procesadas', 0),
        'actividades_crd': total_crd,
        'actividades_plan': total_plan,
        'actividades_retraso': total_retr,
    }