#spme_monitor_estados/constants/eventos.py
from django.db import models
"""
Eventos soportados por el sistema de notificaciones
"""

class CategoriaEvento(models.TextChoices):
    """Categorías de eventos"""
    VALIDACION = 'validacion', 'Validación de Informes'
    SEGURIDAD = 'seguridad', 'Seguridad y Cuenta'
    RECORDATORIO = 'recordatorio', 'Recordatorios'
    SISTEMA = 'sistema', 'Notificaciones del Sistema'
    REPORTE = 'reporte', 'Reportes y Exportaciones'


class EventoMonitor:
    """
    Eventos del sistema de monitoreo
    """
    # ============================================================
    # 1. CATEGORÍA: VALIDACIÓN DE INFORMES
    # ============================================================
    VALIDACION_PENDIENTE = 'validacion_pendiente'
    VALIDACION_APROBADA = 'validacion_aprobada'
    VALIDACION_RECHAZADA = 'validacion_rechazada'
    VALIDACION_OBSERVADA = 'validacion_observada'

    # Para actividades y tareas específicas
    VALIDACION_ACTIVIDAD_PENDIENTE = 'validacion_actividad_pendiente'
    VALIDACION_ACTIVIDAD_APROBADA = 'validacion_actividad_aprobada'
    VALIDACION_ACTIVIDAD_RECHAZADA = 'validacion_actividad_rechazada'
    VALIDACION_ACTIVIDAD_OBSERVADA = 'validacion_actividad_observada'
    
    VALIDACION_TAREA_PENDIENTE = 'validacion_tarea_pendiente'
    VALIDACION_TAREA_APROBADA = 'validacion_tarea_aprobada'
    VALIDACION_TAREA_RECHAZADA = 'validacion_tarea_rechazada'
    VALIDACION_TAREA_OBSERVADA = 'validacion_tarea_observada'

    # ============================================================
    # 2. CATEGORÍA: SEGURIDAD Y CUENTA
    # ============================================================
    USUARIO_BIENVENIDA = 'usuario_bienvenida'
    PASSWORD_RECUPERACION = 'password_recuperacion'
    PASSWORD_CAMBIADO = 'password_cambiado'
    LOGIN_NUEVO_DISPOSITIVO = 'login_nuevo_dispositivo'
    CUENTA_BLOQUEADA = 'cuenta_bloqueada'
    CUENTA_ACTIVADA = 'cuenta_activada'
    EMAIL_VERIFICACION = 'email_verificacion'

    # ============================================================
    # 3. CATEGORÍA: RECORDATORIOS
    # ============================================================
    RECORDATORIO_SEMANAL = 'recordatorio_semanal'
    TAREA_POR_VENCER = 'tarea_por_vencer'
    TAREA_VENCIDA = 'tarea_vencida'  # Ya existe como 'vencida'
    ACTIVIDAD_INACTIVA = 'actividad_inactiva'
    RESUMEN_MENSUAL = 'resumen_mensual'
    ACTIVIDAD_PROXIMO_INICIO = 'actividad_proximo_inicio'  # Ya existe

    # ============================================================
    # 4. CATEGORÍA: NOTIFICACIONES DEL SISTEMA
    # ============================================================
    SISTEMA_ERROR = 'sistema_error'
    MANTENIMIENTO_PROGRAMADO = 'mantenimiento_programado'
    NUEVO_COMENTARIO = 'nuevo_comentario'
    TAREA_ASIGNADA = 'tarea_asignada'
    ACTIVIDAD_ASIGNADA = 'actividad_asignada'
    DOCUMENTO_CARGADO = 'documento_cargado'

    # ============================================================
    # 5. CATEGORÍA: REPORTES Y EXPORTACIONES
    # ============================================================
    REPORTE_LISTO = 'reporte_listo'
    EXPORTACION_COMPLETA = 'exportacion_completa'
    REPORTE_PROGRAMADO = 'reporte_programado'

    # ============================================================
    # CONFIGURACIÓN DE PRIORIDADES
    # ============================================================
    PRIORIDADES = {
        # Validación (Crítica: 4, Alta: 3)
        VALIDACION_PENDIENTE: 3,
        VALIDACION_APROBADA: 2,
        VALIDACION_RECHAZADA: 4,
        VALIDACION_OBSERVADA: 3,
        
        # Seguridad (Crítica para acciones del usuario)
        USUARIO_BIENVENIDA: 3,
        PASSWORD_RECUPERACION: 4,
        PASSWORD_CAMBIADO: 2,
        LOGIN_NUEVO_DISPOSITIVO: 2,
        CUENTA_BLOQUEADA: 4,
        EMAIL_VERIFICACION: 3,
        
        # Recordatorios
        RECORDATORIO_SEMANAL: 2,
        TAREA_POR_VENCER: 3,
        ACTIVIDAD_INACTIVA: 2,
        RESUMEN_MENSUAL: 1,
        
        # Sistema
        SISTEMA_ERROR: 4,
        MANTENIMIENTO_PROGRAMADO: 3,
        NUEVO_COMENTARIO: 2,
        TAREA_ASIGNADA: 3,
        
        # Reportes
        REPORTE_LISTO: 2,
        EXPORTACION_COMPLETA: 1,
        REPORTE_PROGRAMADO: 1,
    }

    # ============================================================
    # ICONOS POR EVENTO
    # ============================================================
    ICONOS = {
        # Validación
        VALIDACION_PENDIENTE: '📝',
        VALIDACION_APROBADA: '✅',
        VALIDACION_RECHAZADA: '❌',
        VALIDACION_OBSERVADA: '👁️',
        
        # Seguridad
        USUARIO_BIENVENIDA: '🎉',
        PASSWORD_RECUPERACION: '🔑',
        PASSWORD_CAMBIADO: '🔒',
        LOGIN_NUEVO_DISPOSITIVO: '💻',
        CUENTA_BLOQUEADA: '🚫',
        EMAIL_VERIFICACION: '✉️',
        
        # Recordatorios
        RECORDATORIO_SEMANAL: '📅',
        TAREA_POR_VENCER: '⏰',
        ACTIVIDAD_INACTIVA: '💤',
        RESUMEN_MENSUAL: '📊',
        
        # Sistema
        SISTEMA_ERROR: '🔥',
        MANTENIMIENTO_PROGRAMADO: '🔧',
        NUEVO_COMENTARIO: '💬',
        TAREA_ASIGNADA: '📋',
        
        # Reportes
        REPORTE_LISTO: '📄',
        EXPORTACION_COMPLETA: '💾',
        REPORTE_PROGRAMADO: '📅',
    }

    # ============================================================
    # CATEGORÍA DE CADA EVENTO
    # ============================================================

    CATEGORIAS = {
        VALIDACION_PENDIENTE: CategoriaEvento.VALIDACION,
        VALIDACION_APROBADA: CategoriaEvento.VALIDACION,
        VALIDACION_RECHAZADA: CategoriaEvento.VALIDACION,
        VALIDACION_OBSERVADA: CategoriaEvento.VALIDACION,
        
        USUARIO_BIENVENIDA: CategoriaEvento.SEGURIDAD,
        PASSWORD_RECUPERACION: CategoriaEvento.SEGURIDAD,
        PASSWORD_CAMBIADO: CategoriaEvento.SEGURIDAD,
        LOGIN_NUEVO_DISPOSITIVO: CategoriaEvento.SEGURIDAD,
        
        RECORDATORIO_SEMANAL: CategoriaEvento.RECORDATORIO,
        RESUMEN_MENSUAL: CategoriaEvento.RECORDATORIO,
        
        SISTEMA_ERROR: CategoriaEvento.SISTEMA,
        MANTENIMIENTO_PROGRAMADO: CategoriaEvento.SISTEMA,
        
        REPORTE_LISTO: CategoriaEvento.REPORTE,
    }
    
    
    