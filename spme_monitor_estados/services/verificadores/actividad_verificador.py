# servicios/verificadores/actividad_verificador.py
# VERSIÓN 2.1 - Regla 2 con notificaciones por email

from ..base.verificador_base import VerificadorBase
from spme_actividades.models import Actividad
from spme_monitoreo.models import (
    SolicitudFondos, SolicitudReembolso, 
    SolicitudViaje, SolicitudPagoDirecto
)
from ..notificadores.notificador_email_lotes import NotificadorEmailLotes
from ..historial.historial_service import HistorialService
from django.db import models
import logging

logger = logging.getLogger(__name__)

class ActividadVerificador(VerificadorBase):
    """
    Verificador para Actividades - VERSIÓN 2.1
    REGLA 1: CRD - Solo informar (cambio manual)
    REGLA 2: PLAN - Notificaciones y cambios automáticos con EMAILS
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.notificador_email = NotificadorEmailLotes(config)
    
    def obtener_queryset(self):
        """
        Obtiene todas las actividades activas
        """
        queryset = Actividad.objects.filter(
            estaInactiva=False
        ).select_related('responsable', 'tipo')
        
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
        Verifica cada actividad aplicando las reglas de negocio
        """
        # Información básica
        logger.info(f"🔍 Actividad: {actividad.codigo}")
        logger.info(f"   • Nombre: {actividad.nombreCorto}")
        logger.info(f"   • Estado actual: {actividad.estado}")
        logger.info(f"   • Responsable: {actividad.responsable or 'No asignado'}")
        
        # ============================================================
        # REGLA 1: ACTIVIDADES EN CRD - Solo informar
        # ============================================================
        if actividad.estado == 'CRD':
            logger.info("   🟢 REGLA 1: Actividad CRD - Pendiente de planificación manual")
            return self._resultado_vacio()
        
        # ============================================================
        # REGLA 2: ACTIVIDADES EN PLAN
        # ============================================================
        elif actividad.estado == 'PLAN':
            logger.info("   🔵 REGLA 2: Actividad en PLAN")
            
            # Verificar si tiene fecha de inicio
            if not actividad.fecha_inicio:
                logger.info("   • ⚠️ Sin fecha de inicio definida")
                return self._resultado_vacio()
            
            dias_para_inicio = (actividad.fecha_inicio - self.hoy).days
            logger.info(f"   • Fecha inicio: {actividad.fecha_inicio} (en {dias_para_inicio} días)")
            
            # ========================================================
            # CASO 2.1: Fecha de inicio en el futuro (notificaciones)
            # ========================================================
            if dias_para_inicio > 0 and dias_para_inicio <= 5:
                return self._notificar_proximo_inicio(actividad, dias_para_inicio)
            
            # ========================================================
            # CASO 2.2: Fecha de inicio pasada
            # ========================================================
            elif dias_para_inicio < 0:
                return self._verificar_inicio_retrasado(actividad, abs(dias_para_inicio))
            
            elif dias_para_inicio == 0:
                logger.info("   • 🟢 ¡INICIA HOY!")
        
        # Otros estados (pendientes de reglas futuras)
        else:
            logger.info(f"   • Estado {actividad.estado} (pendiente reglas futuras)")
        
        logger.info("-" * 40)
        return self._resultado_vacio()
    
    # ================================================================
    # MÉTODOS AUXILIARES PARA REGLA 2
    # ================================================================
    
    def _notificar_proximo_inicio(self, actividad, dias_para_inicio):
        """
        Caso 2.1: Notificar próximos inicios (1-5 días)
        """
        logger.info(f"   • 📧 NOTIFICACIÓN: Actividad próxima a iniciar")
        logger.info(f"   • Faltan {dias_para_inicio} días para el inicio")
        
        # ENCOLAR EMAIL
        email = self.notificador_email.notificar(
            tipo_entidad='actividad',
            evento='proximo_inicio',
            entidad=actividad,
            contexto={'dias': dias_para_inicio}
        )
        
        emails_encolados = 1 if email else 0
        
        return {
            'cambio_realizado': False,
            'cambio': None,
            'notificaciones': 0,  # Las notificaciones internas se cuentan aparte
            'emails_encolados': emails_encolados,
            'tipo_notificacion': 'proximo_inicio',
            'dias_restantes': dias_para_inicio
        }
    
    def _verificar_inicio_retrasado(self, actividad, dias_retraso):
        """
        Caso 2.2: Fecha de inicio pasada - Verificar documentos
        """
        logger.info(f"   • ⚠️ Fecha de inicio pasada ({dias_retraso} días de retraso)")
        
        # Verificar si existen solicitudes relacionadas
        tiene_solicitudes = self._tiene_solicitudes_activas(actividad)
        
        if tiene_solicitudes:
            # CASO 2.2.1: Tiene solicitudes → Pasa a EJEC
            logger.info(f"   • ✅ TIENE SOLICITUDES ACTIVAS - Cambiando a EJEC")
            return self._cambiar_a_ejec(actividad, dias_retraso)
        else:
            # CASO 2.2.2: No tiene solicitudes → Pasa a RETR
            logger.info(f"   • ❌ NO TIENE SOLICITUDES - Cambiando a RETR")
            return self._cambiar_a_retr(actividad, dias_retraso)
    
    def _tiene_solicitudes_activas(self, actividad):
        """
        Verifica si la actividad tiene solicitudes activas
        """
        # Verificar SolicitudFondos
        if SolicitudFondos.objects.filter(actividad=actividad).exists():
            logger.info(f"   • • Encontrada Solicitud de Fondos")
            return True
        
        # Verificar SolicitudReembolso
        if SolicitudReembolso.objects.filter(actividad=actividad).exists():
            logger.info(f"   • • Encontrada Solicitud de Reembolso")
            return True
        
        # Verificar SolicitudViaje
        if SolicitudViaje.objects.filter(actividad=actividad).exists():
            logger.info(f"   • • Encontrada Solicitud de Viaje")
            return True
        
        # Verificar SolicitudPagoDirecto
        if SolicitudPagoDirecto.objects.filter(actividad=actividad).exists():
            logger.info(f"   • • Encontrada Solicitud de Pago Directo")
            return True
        
        return False
    
    def _cambiar_a_ejec(self, actividad, dias_retraso):
        """
        Cambia PLAN → EJEC (por tener solicitudes)
        Y envía email al responsable
        """
        estado_anterior = actividad.estado
        actividad.estado = 'EJEC'
        actividad.gradoEjecucion = 'En ejecución'
        actividad.save()
        
        logger.info(f"   • ✅ CAMBIO: {estado_anterior} → EJEC (por solicitudes activas)")
        
        # REGISTRAR EN HISTORIAL
        HistorialService.registrar_cambio(
            tipo_entidad='actividad',
            entidad=actividad,
            cambio_info={
                'estado_anterior': estado_anterior,
                'estado_nuevo': 'EJEC',
                'motivo': f'Fecha de inicio pasada {dias_retraso} días con solicitudes activas',
                'automatico': True,
                'detalles': {'dias_retraso': dias_retraso}
            }
        )
        
        # ENCOLAR EMAIL
        email = self.notificador_email.notificar(
            tipo_entidad='actividad',
            evento='inicio_ejecucion',
            entidad=actividad,
            contexto={'dias_retraso': dias_retraso, 'con_solicitudes': True}
        )
        
        emails_encolados = 1 if email else 0
        
        return {
            'cambio_realizado': True,
            'cambio': {
                'estado_anterior': estado_anterior,
                'estado_nuevo': 'EJEC',
                'motivo': f'Fecha de inicio pasada {dias_retraso} días con solicitudes activas',
                'tipo_cambio': 'inicio_con_solicitudes',
                'dias_retraso': dias_retraso
            },
            'notificaciones': 0,
            'emails_encolados': emails_encolados
        }
    
    def _cambiar_a_retr(self, actividad, dias_retraso):
        """
        Cambia PLAN → RETR (sin solicitudes)
        Y envía email al responsable
        """
        estado_anterior = actividad.estado
        actividad.estado = 'RETR'
        actividad.gradoEjecucion = f'RETRASO: {dias_retraso} días'
        actividad.save()
        
        logger.info(f"   • 🔴 CAMBIO: {estado_anterior} → RETR (sin solicitudes)")
        
        # REGISTRAR EN HISTORIAL
        HistorialService.registrar_cambio(
            tipo_entidad='actividad',
            entidad=actividad,
            cambio_info={
                'estado_anterior': estado_anterior,
                'estado_nuevo': 'RETR',
                'motivo': f'Fecha de inicio pasada {dias_retraso} días sin solicitudes',
                'automatico': True,
                'detalles': {'dias_retraso': dias_retraso}
            }
        )
        
        # ENCOLAR EMAIL - Determinar si es retraso crítico (>15 días)
        evento = 'retraso_critico' if dias_retraso >= 15 else 'retraso'
        email = self.notificador_email.notificar(
            tipo_entidad='actividad',
            evento=evento,
            entidad=actividad,
            contexto={'dias': dias_retraso}
        )
        
        emails_encolados = 1 if email else 0
        
        return {
            'cambio_realizado': True,
            'cambio': {
                'estado_anterior': estado_anterior,
                'estado_nuevo': 'RETR',
                'motivo': f'Fecha de inicio pasada {dias_retraso} días sin solicitudes',
                'dias_retraso': dias_retraso
            },
            'notificaciones': 0,
            'emails_encolados': emails_encolados
        }
    
    def _resultado_vacio(self):
        """Retorna un resultado sin cambios"""
        return {
            'cambio_realizado': False,
            'cambio': None,
            'notificaciones': 0,
            'emails_encolados': 0
        }
    
    # ================================================================
    # MÉTODOS AUXILIARES PARA ESTADOS ESPECÍFICOS
    # ================================================================
    
    def _obtener_crd(self):
        """Obtiene solo actividades en CRD"""
        return Actividad.objects.filter(estaInactiva=False, estado='CRD')
    
    def _obtener_plan(self):
        """Obtiene solo actividades en PLAN"""
        return Actividad.objects.filter(estaInactiva=False, estado='PLAN')
    
    def _obtener_retraso(self):
        """Obtiene solo actividades en RETR"""
        return Actividad.objects.filter(estaInactiva=False, estado='RETR')


def procesar_actividades(config):
    """
    Función de entrada para probar el verificador
    Versión 2.1 - Reglas CRD y PLAN con emails
    """

     # ===== LOGS DE VERIFICACIÓN =====
    print("🔴🔴🔴 DEPURACIÓN: procesar_actividades() SÍ se está ejecutando 🔴🔴🔴")
    logger.info("🔴🔴🔴 DEPURACIÓN: procesar_actividades() SÍ se está ejecutando 🔴🔴🔴")
    print(f"📌 Config recibida: {config}")
    print(f"📌 Tipo de config: {type(config)}")
    print(f"📌 Atributos de config: {dir(config)}")
    # ================================
    logger.info("="*60)
    logger.info("🚀 INICIANDO VERIFICADOR DE ACTIVIDADES - VERSIÓN 2.1")
    logger.info("📋 REGLAS ACTIVAS: CRD (informativa) + PLAN (con emails)")
    logger.info("="*60)
    
    verificador = ActividadVerificador(config)
    
    # ============================================================
    # REGLA 1: Actividades CRD
    # ============================================================
    actividades_crd = verificador._obtener_crd()
    total_crd = actividades_crd.count()
    logger.info(f"\n📌 REGLA 1 - CRD: {total_crd} actividades")
    
    # ============================================================
    # REGLA 2: Actividades PLAN
    # ============================================================
    actividades_plan = verificador._obtener_plan()
    total_plan = actividades_plan.count()
    
    logger.info(f"\n📌 REGLA 2 - PLAN: {total_plan} actividades")
    
    if total_plan > 0:
        # Analizar PLAN sin ejecutar cambios (solo vista previa)
        logger.info("\n🔍 ANÁLISIS PREVIO DE ACTIVIDADES PLAN:")
        for act in actividades_plan:
            if act.fecha_inicio:
                dias = (act.fecha_inicio - verificador.hoy).days
                if 0 < dias <= 5:
                    logger.info(f"   • {act.codigo}: PRÓXIMO INICIO en {dias} días")
                elif dias < 0:
                    tiene_solicitudes = verificador._tiene_solicitudes_activas(act)
                    estado = "CON SOLICITUDES (→ EJEC)" if tiene_solicitudes else "SIN SOLICITUDES (→ RETR)"
                    logger.info(f"   • {act.codigo}: RETRASO {abs(dias)} días - {estado}")
    
    # ============================================================
    # PROCESAR TODAS LAS ACTIVIDADES (ejecuta cambios reales)
    # ============================================================
    logger.info("\n" + "="*60)
    logger.info("🔄 EJECUTANDO VERIFICACIÓN CON CAMBIOS REALES")
    logger.info("="*60)
    
    resultados = verificador.procesar_todas()
    
    # ============================================================
    # RESUMEN FINAL
    # ============================================================
    logger.info("\n" + "="*60)
    logger.info("📊 RESUMEN FINAL DE VERIFICACIÓN")
    logger.info("="*60)
    
    logger.info(f"\n📌 TOTAL PROCESADAS: {resultados.get('procesadas', 0)}")
    logger.info(f"📌 CAMBIOS REALIZADOS: {resultados.get('cambios', 0)}")
    logger.info(f"📌 EMAILS ENCOLADOS: {resultados.get('emails_encolados', 0)}")
    
    if resultados.get('detalles'):
        logger.info("\n📋 DETALLE DE CAMBIOS:")
        for detalle in resultados['detalles']:
            cambio = detalle['cambio']
            logger.info(f"   • {detalle['codigo']}: {cambio['estado_anterior']} → {cambio['estado_nuevo']}")
            logger.info(f"     Motivo: {cambio['motivo']}")
    
    logger.info("\n" + "="*60)
    logger.info("✅ VERIFICADOR COMPLETADO")
    logger.info("="*60)
    
    return {
        'procesadas': resultados.get('procesadas', 0),
        'cambios': resultados.get('cambios', 0),
        'emails_encolados': resultados.get('emails_encolados', 0),
        'actividades_crd': total_crd,
        'actividades_plan': total_plan,
        'actividades_retraso': verificador._obtener_retraso().count()
    }