#spme_monitor_estados/utils/encolar.py
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

"""
Función universal para encolar emails desde cualquier aplicación.
Versión 2.5 - Todas las funciones de encolado para todos los templates.
"""

def encolar_email(
    destinatario,
    asunto,
    template_html=None,
    contexto=None,
    cuerpo_html=None,
    cuerpo_texto=None,
    prioridad=2,
    programado_para=None,
    tipo_entidad=None,
    entidad_id=None,
    evento=None
):
    """Función base para encolar emails."""
    from ..models.cola_email import EmailEnCola
    if not destinatario or not asunto:
        logger.error("❌ Destinatario o asunto vacío")
        return None
    
    contexto = contexto or {}
    
    if template_html:
        try:
            cuerpo_html = render_to_string(template_html, contexto)
            cuerpo_texto = strip_tags(cuerpo_html)
        except Exception as e:
            logger.error(f"❌ Error renderizando template {template_html}: {e}")
            raise
            #return None
    else:
        if cuerpo_html and not cuerpo_texto:
            cuerpo_texto = strip_tags(cuerpo_html)
        if cuerpo_texto and not cuerpo_html:
            cuerpo_html = f"<p>{cuerpo_texto.replace(chr(10), '<br>')}</p>"
    
    if not cuerpo_html:
        logger.error("❌ Sin contenido")
        return None
    
    if programado_para is None:
        tiempos = {4: 0, 3: 5, 2: 15, 1: 30}
        minutos = tiempos.get(prioridad, 15)
        programado_para = timezone.now() + timedelta(minutes=minutos)
    
    try:
        email = EmailEnCola.objects.create(
            destinatario=destinatario,
            asunto=asunto,
            cuerpo_html=cuerpo_html,
            cuerpo_texto=cuerpo_texto,
            prioridad=prioridad,
            programado_para=programado_para,
            tipo_entidad=tipo_entidad or '',
            entidad_id=entidad_id,
            evento=evento or ''
        )
        logger.info(f"📧 Email ENCOLADO: {asunto} → {destinatario}")
        return email
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise
        #return None


# ============================================================
# 1. FUNCIONES DE VALIDACIÓN (5 funciones)
# ============================================================

def encolar_validacion_pendiente(informe, tipo, validador, enlace_aprobacion=None, enlace_rechazo=None, enlace_observacion=None, enlace_ver_detalle=None, site_url=None):
    """Notifica al validador que hay un informe pendiente."""
    from spme_actividades.models import Actividad, TareaActividad
    site_url = site_url or 'http://localhost:8000'

    #Cargar el objeto real
    if tipo == 'actividad':
        entidad = informe.actividad if hasattr(informe.actividad, 'codigo') else Actividad.objects.get(id=informe.actividad)
    else:
        entidad = informe.tarea if hasattr(informe.tarea, 'codigo') else TareaActividad.objects.get(id=informe.tarea)
    
    if not enlace_ver_detalle:
        enlace_ver_detalle = f"{site_url}/ver/{tipo}/{entidad.id}"
    
    contexto = {
        'tipo': tipo, 'entidad': entidad, 'informe': informe, 'validador': validador,
        'enlace_aprobacion': enlace_aprobacion, 'enlace_rechazo': enlace_rechazo,
        'enlace_observacion': enlace_observacion, 'enlace_ver_detalle': enlace_ver_detalle,
        'site_url': site_url, 'fecha': timezone.now(), 'icono': '📝',
        'titulo': 'Validación Pendiente', 'color': '#4CAF50'
    }

    return encolar_email(
        destinatario=validador.correo if hasattr(validador, 'correo') else validador.email,
        asunto=f"📝 {tipo.title()} pendiente de validación - {entidad.codigo}",
        template_html='emails/validacion/pendiente.html', contexto=contexto,
        prioridad=3, tipo_entidad=tipo, entidad_id=entidad.id, evento='validacion_pendiente'
    )


def encolar_validacion_aprobada(informe, tipo, validador, comentarios=None, enlace_actividad=None, site_url=None):
    """Notifica al responsable que su informe fue aprobado."""
    site_url = site_url or 'http://localhost:8000'
    entidad = informe.actividad if tipo == 'actividad' else informe.tarea
    responsable = entidad.responsable
    if not enlace_actividad:
        enlace_actividad = f"{site_url}/ver/{tipo}/{entidad.id}"
    
    contexto = {
        'tipo': tipo, 'entidad': entidad, 'informe': informe, 'validador': validador,
        'comentarios': comentarios, 'enlace_actividad': enlace_actividad,
        'site_url': site_url, 'fecha': timezone.now(), 'icono': '✅',
        'titulo': 'Informe Aprobado', 'color': '#4CAF50'
    }
    return encolar_email(
        destinatario=responsable.correo if hasattr(responsable, 'correo') else responsable.email,
        asunto=f"✅ Informe Aprobado - {entidad.codigo}",
        template_html='emails/validacion/aprobada.html', contexto=contexto,
        prioridad=3, tipo_entidad=tipo, entidad_id=entidad.id, evento='validacion_aprobada'
    )


def encolar_validacion_rechazada(informe, tipo, validador, motivo, enlace_actividad=None, site_url=None):
    """Notifica al responsable que su informe fue rechazado."""
    site_url = site_url or 'http://localhost:8000'
    entidad = informe.actividad if tipo == 'actividad' else informe.tarea
    responsable = entidad.responsable
    if not enlace_actividad:
        enlace_actividad = f"{site_url}/ver/{tipo}/{entidad.id}"
    
    contexto = {
        'tipo': tipo, 'entidad': entidad, 'informe': informe, 'validador': validador,
        'motivo': motivo, 'enlace_actividad': enlace_actividad,
        'site_url': site_url, 'fecha': timezone.now(), 'icono': '❌',
        'titulo': 'Informe Rechazado', 'color': '#f44336'
    }
    return encolar_email(
        destinatario=responsable.correo if hasattr(responsable, 'correo') else responsable.email,
        asunto=f"❌ Informe Rechazado - {entidad.codigo}",
        template_html='emails/validacion/rechazada.html', contexto=contexto,
        prioridad=4, tipo_entidad=tipo, entidad_id=entidad.id, evento='validacion_rechazada'
    )


def encolar_validacion_observada(informe, tipo, validador, observaciones, enlace_actividad=None, site_url=None):
    """Notifica al responsable que su informe tiene observaciones."""
    site_url = site_url or 'http://localhost:8000'
    entidad = informe.actividad if tipo == 'actividad' else informe.tarea
    responsable = entidad.responsable
    if not enlace_actividad:
        enlace_actividad = f"{site_url}/ver/{tipo}/{entidad.id}"
    
    contexto = {
        'tipo': tipo, 'entidad': entidad, 'informe': informe, 'validador': validador,
        'observaciones': observaciones, 'enlace_actividad': enlace_actividad,
        'site_url': site_url, 'fecha': timezone.now(), 'icono': '👁️',
        'titulo': 'Informe con Observaciones', 'color': '#ff9800'
    }
    return encolar_email(
        destinatario=responsable.correo if hasattr(responsable, 'correo') else responsable.email,
        asunto=f"👁️ Informe con Observaciones - {entidad.codigo}",
        template_html='emails/validacion/observada.html', contexto=contexto,
        prioridad=3, tipo_entidad=tipo, entidad_id=entidad.id, evento='validacion_observada'
    )


def encolar_confirmacion_validador(informe, tipo, validador, accion, enlace_ver_detalle=None, site_url=None):
    """Envía confirmación al validador después de realizar una acción."""
    site_url = site_url or 'http://localhost:8000'
    entidad = informe.actividad if tipo == 'actividad' else informe.tarea
    if not enlace_ver_detalle:
        enlace_ver_detalle = f"{site_url}/ver/{tipo}/{entidad.id}"
    
    acciones_texto = {'aprobado': 'aprobado', 'rechazado': 'rechazado', 'observado': 'observado'}
    
    contexto = {
        'tipo': tipo, 'entidad': entidad, 'informe': informe, 'validador': validador,
        'accion_texto': acciones_texto.get(accion, accion), 'enlace_ver_detalle': enlace_ver_detalle,
        'site_url': site_url, 'fecha': timezone.now(), 'icono': '✅',
        'titulo': 'Confirmación', 'color': '#2196F3'
    }
    return encolar_email(
        destinatario=validador.correo if hasattr(validador, 'correo') else validador.email,
        asunto=f"✅ Confirmación: Informe {accion} - {entidad.codigo}",
        template_html='emails/validacion/confirmacion_validador.html', contexto=contexto,
        prioridad=2, tipo_entidad=tipo, entidad_id=entidad.id, evento='confirmacion_validador'
    )


# ============================================================
# 2. FUNCIONES DE SEGURIDAD (5 funciones)
# ============================================================

def encolar_bienvenida(usuario, password_temporal=None, enlace_login=None, site_url=None):
    """Email de bienvenida para nuevo usuario."""
    site_url = site_url or 'http://localhost:8000'
    enlace_login = enlace_login or f"{site_url}/login"
    contexto = {
        'usuario': usuario, 'password_temporal': password_temporal,
        'enlace_login': enlace_login, 'site_url': site_url,
        'icono': '🎉', 'titulo': '¡Bienvenido!', 'color': '#4CAF50'
    }
    nombre = f"{usuario.nombre} {usuario.paterno}" if hasattr(usuario, 'nombre') else usuario.username
    return encolar_email(
        destinatario=usuario.correo if hasattr(usuario, 'correo') else usuario.email,
        asunto=f"🎉 Bienvenido a SPME - {nombre}",
        template_html='emails/seguridad/bienvenida.html', contexto=contexto,
        prioridad=3, tipo_entidad='usuario', entidad_id=usuario.id, evento='bienvenida'
    )


def encolar_recuperacion_password(usuario, token, ip_address=None, enlace_reset=None, site_url=None):
    """Email para recuperación de contraseña."""
    site_url = site_url or 'http://localhost:8000'
    enlace_reset = enlace_reset or f"{site_url}/reset-password/{token}"
    contexto = {
        'usuario': usuario, 'token': token, 'ip_address': ip_address,
        'enlace_reset': enlace_reset, 'site_url': site_url, 'validez_horas': 24,
        'fecha': timezone.now(), 'icono': '🔑', 'titulo': 'Recuperación de Contraseña',
        'color': '#2196F3'
    }
    return encolar_email(
        destinatario=usuario.correo if hasattr(usuario, 'correo') else usuario.email,
        asunto="🔑 Recuperación de contraseña - SPME",
        template_html='emails/seguridad/recuperacion_password.html', contexto=contexto,
        prioridad=4, tipo_entidad='usuario', entidad_id=usuario.id, evento='recuperacion_password'
    )


def encolar_password_cambiado(usuario, ip_address=None, enlace_login=None, site_url=None):
    """Notifica que la contraseña fue cambiada exitosamente."""
    site_url = site_url or 'http://localhost:8000'
    enlace_login = enlace_login or f"{site_url}/login"
    contexto = {
        'usuario': usuario, 'ip_address': ip_address, 'enlace_login': enlace_login,
        'fecha_cambio': timezone.now(), 'site_url': site_url, 'icono': '🔒',
        'titulo': 'Contraseña Cambiada', 'color': '#2196F3'
    }
    return encolar_email(
        destinatario=usuario.correo if hasattr(usuario, 'correo') else usuario.email,
        asunto="🔒 Tu contraseña ha sido cambiada",
        template_html='emails/seguridad/password_cambiado.html', contexto=contexto,
        prioridad=2, tipo_entidad='usuario', entidad_id=usuario.id, evento='password_cambiado'
    )


def encolar_nuevo_login(usuario, dispositivo, ip_address, ubicacion=None, enlace_cambio_password=None, site_url=None):
    """Alerta de nuevo inicio de sesión desde dispositivo desconocido."""
    site_url = site_url or 'http://localhost:8000'
    enlace_cambio_password = enlace_cambio_password or f"{site_url}/cambiar-password"
    contexto = {
        'usuario': usuario, 'dispositivo': dispositivo, 'ip_address': ip_address,
        'ubicacion': ubicacion, 'enlace_cambio_password': enlace_cambio_password,
        'fecha_login': timezone.now(), 'site_url': site_url, 'icono': '💻',
        'titulo': 'Nuevo Inicio de Sesión', 'color': '#ff9800'
    }
    return encolar_email(
        destinatario=usuario.correo if hasattr(usuario, 'correo') else usuario.email,
        asunto="💻 Nuevo inicio de sesión en tu cuenta",
        template_html='emails/seguridad/nuevo_login.html', contexto=contexto,
        prioridad=2, tipo_entidad='usuario', entidad_id=usuario.id, evento='nuevo_login'
    )


def encolar_cuenta_bloqueada(usuario, motivo, es_notificacion_admin=False, enlace_soporte=None, site_url=None):
    """Notifica que la cuenta fue bloqueada."""
    site_url = site_url or 'http://localhost:8000'
    enlace_soporte = enlace_soporte or f"{site_url}/soporte"
    contexto = {
        'usuario': usuario, 'motivo': motivo, 'es_notificacion_admin': es_notificacion_admin,
        'enlace_soporte': enlace_soporte, 'fecha_bloqueo': timezone.now(),
        'site_url': site_url, 'icono': '🚫', 'titulo': 'Cuenta Bloqueada', 'color': '#f44336'
    }
    return encolar_email(
        destinatario=usuario.correo if hasattr(usuario, 'correo') else usuario.email,
        asunto="🚫 Tu cuenta ha sido bloqueada",
        template_html='emails/seguridad/cuenta_bloqueada.html', contexto=contexto,
        prioridad=4, tipo_entidad='usuario', entidad_id=usuario.id, evento='cuenta_bloqueada'
    )


# ============================================================
# 3. FUNCIONES DE RECORDATORIOS (4 funciones)
# ============================================================

def encolar_tarea_por_vencer(tarea, dias_restantes, enlace_tarea=None, site_url=None):
    """Recordatorio de tarea que está por vencer."""
    site_url = site_url or 'http://localhost:8000'
    enlace_tarea = enlace_tarea or f"{site_url}/tareas/{tarea.id}"
    contexto = {
        'tarea': tarea, 'dias_restantes': dias_restantes, 'enlace_tarea': enlace_tarea,
        'site_url': site_url, 'icono': '⏰', 'titulo': 'Tarea por Vencer', 'color': '#ff9800'
    }
    return encolar_email(
        destinatario=tarea.responsable.correo if hasattr(tarea.responsable, 'correo') else tarea.responsable.email,
        asunto=f"⏰ Tarea por vencer - {tarea.codigo}",
        template_html='emails/recordatorios/tarea_por_vencer.html', contexto=contexto,
        prioridad=3, tipo_entidad='tarea', entidad_id=tarea.id, evento='tarea_por_vencer'
    )


def encolar_actividad_inactiva(actividad, dias_inactiva, enlace_actividad=None, enlace_informe=None, site_url=None):
    """Notifica que una actividad lleva mucho tiempo sin actualizarse."""
    site_url = site_url or 'http://localhost:8000'
    enlace_actividad = enlace_actividad or f"{site_url}/actividades/{actividad.id}"
    enlace_informe = enlace_informe or f"{site_url}/actividades/{actividad.id}/informe"
    contexto = {
        'actividad': actividad, 'dias_inactiva': dias_inactiva,
        'enlace_actividad': enlace_actividad, 'enlace_informe': enlace_informe,
        'site_url': site_url, 'icono': '💤', 'titulo': 'Actividad Inactiva', 'color': '#ff9800'
    }
    return encolar_email(
        destinatario=actividad.responsable.correo if hasattr(actividad.responsable, 'correo') else actividad.responsable.email,
        asunto=f"💤 Actividad inactiva - {actividad.codigo}",
        template_html='emails/recordatorios/actividad_inactiva.html', contexto=contexto,
        prioridad=2, tipo_entidad='actividad', entidad_id=actividad.id, evento='actividad_inactiva'
    )


def encolar_resumen_semanal(usuario, actividades_pendientes, tareas_pendientes, enlace_actividades=None, enlace_tareas=None, enlace_dashboard=None, site_url=None):
    """Resumen semanal de actividades y tareas pendientes."""
    site_url = site_url or 'http://localhost:8000'
    enlace_actividades = enlace_actividades or f"{site_url}/actividades"
    enlace_tareas = enlace_tareas or f"{site_url}/tareas"
    enlace_dashboard = enlace_dashboard or f"{site_url}/dashboard"
    contexto = {
        'usuario': usuario, 'actividades_pendientes': actividades_pendientes, 'tareas_pendientes': tareas_pendientes,
        'total_actividades': len(actividades_pendientes), 'total_tareas': len(tareas_pendientes),
        'enlace_actividades': enlace_actividades, 'enlace_tareas': enlace_tareas, 'enlace_dashboard': enlace_dashboard,
        'semana': timezone.now().isocalendar()[1], 'site_url': site_url,
        'icono': '📅', 'titulo': 'Resumen Semanal', 'color': '#2196F3'
    }
    return encolar_email(
        destinatario=usuario.correo if hasattr(usuario, 'correo') else usuario.email,
        asunto=f"📅 Resumen Semanal - Semana {timezone.now().isocalendar()[1]}",
        template_html='emails/recordatorios/resumen_semanal.html', contexto=contexto,
        prioridad=2, tipo_entidad='usuario', entidad_id=usuario.id, evento='resumen_semanal'
    )


def encolar_resumen_mensual(usuario, estadisticas, enlace_reporte=None, site_url=None):
    """Resumen mensual de actividad del usuario."""
    site_url = site_url or 'http://localhost:8000'
    enlace_reporte = enlace_reporte or f"{site_url}/reportes/mensual"
    contexto = {
        'usuario': usuario, 'estadisticas': estadisticas, 'enlace_reporte': enlace_reporte,
        'mes': timezone.now().strftime('%B %Y'), 'site_url': site_url,
        'icono': '📊', 'titulo': 'Resumen Mensual', 'color': '#4CAF50'
    }
    return encolar_email(
        destinatario=usuario.correo if hasattr(usuario, 'correo') else usuario.email,
        asunto=f"📊 Resumen Mensual - {timezone.now().strftime('%B %Y')}",
        template_html='emails/recordatorios/resumen_mensual.html', contexto=contexto,
        prioridad=1, tipo_entidad='usuario', entidad_id=usuario.id, evento='resumen_mensual'
    )


# ============================================================
# 4. FUNCIONES DE SISTEMA (4 funciones)
# ============================================================

def encolar_error_sistema(error, contexto_error, modulo=None, traceback=None, enlace_logs=None, enlace_reintentar=None, admin_emails=None, site_url=None):
    """Notifica errores críticos del sistema a los administradores."""
    site_url = site_url or 'http://localhost:8000'
    enlace_logs = enlace_logs or f"{site_url}/admin/logs"
    enlace_reintentar = enlace_reintentar or f"{site_url}"
    admin_emails = admin_emails or []
    
    contexto = {
        'error': str(error), 'contexto': contexto_error, 'modulo': modulo,
        'traceback': traceback, 'enlace_logs': enlace_logs, 'enlace_reintentar': enlace_reintentar,
        'fecha_error': timezone.now(), 'site_url': site_url,
        'icono': '🔥', 'titulo': 'Error del Sistema', 'color': '#f44336'
    }
    
    emails_enviados = []
    for admin_email in admin_emails:
        email = encolar_email(
            destinatario=admin_email,
            asunto=f"🔥 Error crítico en {modulo or 'SPME'}",
            template_html='emails/sistema/error_sistema.html', contexto=contexto,
            prioridad=4, tipo_entidad='sistema', evento='error_sistema'
        )
        if email:
            emails_enviados.append(email)
    return emails_enviados


def encolar_mantenimiento(fecha_inicio, fecha_fin, razon, destinatarios, enlace_estado=None, duracion_estimada=None, site_url=None):
    """Notifica mantenimiento programado del sistema."""
    site_url = site_url or 'http://localhost:8000'
    enlace_estado = enlace_estado or f"{site_url}/estado"
    contexto = {
        'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin, 'razon': razon,
        'duracion_estimada': duracion_estimada, 'enlace_estado': enlace_estado,
        'site_url': site_url, 'icono': '🔧', 'titulo': 'Mantenimiento Programado', 'color': '#ff9800'
    }
    
    emails_enviados = []
    for destinatario in destinatarios:
        email = encolar_email(
            destinatario=destinatario,
            asunto="🔧 Mantenimiento programado del sistema",
            template_html='emails/sistema/mantenimiento.html', contexto=contexto,
            prioridad=3, tipo_entidad='sistema', evento='mantenimiento'
        )
        if email:
            emails_enviados.append(email)
    return emails_enviados


def encolar_tarea_asignada(tarea, asignador, mensaje=None, enlace_tarea=None, site_url=None):
    """Notifica que se asignó una nueva tarea."""
    site_url = site_url or 'http://localhost:8000'
    enlace_tarea = enlace_tarea or f"{site_url}/tareas/{tarea.id}"
    contexto = {
        'tarea': tarea, 'asignador': asignador, 'mensaje': mensaje,
        'enlace_tarea': enlace_tarea, 'site_url': site_url,
        'icono': '📋', 'titulo': 'Nueva Tarea Asignada', 'color': '#4CAF50'
    }
    return encolar_email(
        destinatario=tarea.responsable.correo if hasattr(tarea.responsable, 'correo') else tarea.responsable.email,
        asunto=f"📋 Nueva tarea asignada - {tarea.codigo}",
        template_html='emails/sistema/tarea_asignada.html', contexto=contexto,
        prioridad=3, tipo_entidad='tarea', entidad_id=tarea.id, evento='tarea_asignada'
    )


def encolar_nuevo_comentario(entidad, comentario, autor, responsable, enlace_responder=None, site_url=None):
    """Notifica un nuevo comentario en una entidad."""
    site_url = site_url or 'http://localhost:8000'
    tipo_entidad = 'actividad' if hasattr(entidad, 'nombreCorto') else 'tarea'
    enlace_responder = enlace_responder or f"{site_url}/{tipo_entidad}s/{entidad.id}/comentarios"
    contexto = {
        'entidad': entidad, 'comentario': comentario, 'autor': autor,
        'responsable': responsable, 'enlace_responder': enlace_responder,
        'tipo_entidad': tipo_entidad, 'fecha_comentario': timezone.now(),
        'site_url': site_url, 'icono': '💬', 'titulo': 'Nuevo Comentario', 'color': '#2196F3'
    }
    return encolar_email(
        destinatario=responsable.correo if hasattr(responsable, 'correo') else responsable.email,
        asunto=f"💬 Nuevo comentario en {tipo_entidad} {entidad.codigo}",
        template_html='emails/sistema/nuevo_comentario.html', contexto=contexto,
        prioridad=2, tipo_entidad=tipo_entidad, entidad_id=entidad.id, evento='nuevo_comentario'
    )


# ============================================================
# 5. FUNCIONES DE REPORTES (2 funciones)
# ============================================================

def encolar_reporte_listo(usuario, reporte_nombre, enlace_descarga, formato='PDF', tamano=None, validez_dias=7, limite_descargas=5, site_url=None):
    """Notifica que un reporte está listo para descargar."""
    site_url = site_url or 'http://localhost:8000'
    contexto = {
        'usuario': usuario, 'reporte_nombre': reporte_nombre, 'enlace_descarga': enlace_descarga,
        'formato': formato, 'tamano': tamano, 'validez_dias': validez_dias,
        'limite_descargas': limite_descargas, 'fecha': timezone.now(),
        'site_url': site_url, 'icono': '📄', 'titulo': 'Reporte Listo', 'color': '#4CAF50'
    }
    return encolar_email(
        destinatario=usuario.correo if hasattr(usuario, 'correo') else usuario.email,
        asunto=f"📄 Tu reporte '{reporte_nombre}' está listo",
        template_html='emails/reportes/reporte_listo.html', contexto=contexto,
        prioridad=2, tipo_entidad='usuario', entidad_id=usuario.id, evento='reporte_listo'
    )


def encolar_exportacion_lista(usuario, exportacion_nombre, enlace_descarga, registros=None, formato='CSV/Excel', validez_dias=7, enlace_nueva_exportacion=None, site_url=None):
    """Notifica que una exportación de datos está completa."""
    site_url = site_url or 'http://localhost:8000'
    enlace_nueva_exportacion = enlace_nueva_exportacion or f"{site_url}/exportaciones/nueva"
    contexto = {
        'usuario': usuario, 'exportacion_nombre': exportacion_nombre, 'enlace_descarga': enlace_descarga,
        'registros': registros, 'formato': formato, 'validez_dias': validez_dias,
        'enlace_nueva_exportacion': enlace_nueva_exportacion, 'fecha': timezone.now(),
        'site_url': site_url, 'icono': '💾', 'titulo': 'Exportación Lista', 'color': '#2196F3'
    }
    return encolar_email(
        destinatario=usuario.correo if hasattr(usuario, 'correo') else usuario.email,
        asunto=f"💾 Tu exportación '{exportacion_nombre}' está lista",
        template_html='emails/reportes/exportacion_lista.html', contexto=contexto,
        prioridad=1, tipo_entidad='usuario', entidad_id=usuario.id, evento='exportacion_lista'
    )


# ============================================================
# FUNCIÓN ESPECÍFICA PARA SOLICITUD DE FONDOS
# ============================================================

def encolar_validacion_pendiente_sf(solicitud, validador, enlace_ver_detalle=None, site_url=None):
    """
    Notifica al validador que tiene una solicitud de fondos pendiente.
    Versión específica para SolicitudFondos.
    No accede a informe.actividad ni informe.tarea.
    
    Args:
        solicitud: Objeto SolicitudFondos
        validador: Objeto Usuario
        enlace_ver_detalle: URL para ver el detalle
        site_url: URL base del sitio
    """
    site_url = site_url or 'http://localhost:8000'
    
    if not enlace_ver_detalle:
        enlace_ver_detalle = f"{site_url}/solicitudes-fondos/{solicitud.id}"
    
    codigo = solicitud.numeroFormulario or f"SF-{solicitud.id}"
    
    contexto = {
        'tipo': 'solicitud_fondos',
        'entidad': solicitud,
        'solicitud': solicitud,
        'validador': validador,
        'codigo': codigo,
        'monto': solicitud.montoSolicitado,
        'enlace_ver_detalle': enlace_ver_detalle,
        'site_url': site_url,
        'fecha': timezone.now(),
        'icono': '💵',
        'titulo': 'Validación Pendiente - Solicitud de Fondos',
        'color': '#4CAF50'
    }
    
    return encolar_email(
        destinatario=validador.email if hasattr(validador, 'email') else validador.correo,
        asunto=f"💵 Solicitud de Fondos pendiente - {codigo}",
        template_html='emails/validacion/pendiente_sf.html',
        contexto=contexto,
        prioridad=3,
        tipo_entidad='solicitud_fondos',
        entidad_id=solicitud.id,
        evento='validacion_pendiente_sf'
    )

def encolar_confirmacion_validador_sf(solicitud, validador, accion, enlace_ver_detalle=None, site_url=None):
    """
    Confirma al validador que su voto fue registrado.
    Versión específica para SolicitudFondos.
    No accede a informe.actividad ni informe.tarea.
    """
    site_url = site_url or 'http://localhost:8000'
    
    if not enlace_ver_detalle:
        enlace_ver_detalle = f"{site_url}/solicitudes-fondos/{solicitud.id}"
    
    codigo = solicitud.numeroFormulario or f"SF-{solicitud.id}"
    acciones_texto = {'aprobado': 'aprobado', 'rechazado': 'rechazado'}
    
    contexto = {
        'tipo': 'solicitud_fondos',
        'entidad': solicitud,
        'solicitud': solicitud,
        'validador': validador,
        'accion_texto': acciones_texto.get(accion, accion),
        'codigo': codigo,
        'enlace_ver_detalle': enlace_ver_detalle,
        'site_url': site_url,
        'fecha': timezone.now(),
        'icono': '✅',
        'titulo': 'Confirmación de Voto',
        'color': '#2196F3'
    }
    
    return encolar_email(
        destinatario=validador.email if hasattr(validador, 'email') else validador.correo,
        asunto=f"✅ Has {acciones_texto.get(accion, accion).upper()} la solicitud - {codigo}",
        template_html='emails/validacion/confirmacion_validador_sf.html',
        contexto=contexto,
        prioridad=2,
        tipo_entidad='solicitud_fondos',
        entidad_id=solicitud.id,
        evento='confirmacion_validador_sf'
    )

def encolar_validacion_aprobada_sf(solicitud, validador, comentarios=None, enlace_ver_detalle=None, site_url=None):
    """
    Notifica al SOLICITANTE que su solicitud de fondos fue APROBADA.
    Versión específica para SolicitudFondos.
    """
    site_url = site_url or 'http://localhost:8000'
    
    if not enlace_ver_detalle:
        enlace_ver_detalle = f"{site_url}/solicitudes-fondos/{solicitud.id}"
    
    codigo = solicitud.numeroFormulario or f"SF-{solicitud.id}"
    solicitante = solicitud.usuario
    
    contexto = {
        'tipo': 'solicitud_fondos',
        'entidad': solicitud,
        'solicitud': solicitud,
        'solicitante': solicitante,
        'validador': validador,
        'codigo': codigo,
        'monto': solicitud.montoSolicitado,
        'comentarios': comentarios,
        'enlace_ver_detalle': enlace_ver_detalle,
        'site_url': site_url,
        'fecha': timezone.now(),
        'icono': '✅',
        'titulo': 'Solicitud Aprobada',
        'color': '#4CAF50'
    }
    
    return encolar_email(
        destinatario=solicitante.email if hasattr(solicitante, 'email') else solicitante.correo,
        asunto=f"✅ Solicitud APROBADA - {codigo}",
        template_html='emails/validacion/aprobada_sf.html',
        contexto=contexto,
        prioridad=3,
        tipo_entidad='solicitud_fondos',
        entidad_id=solicitud.id,
        evento='validacion_aprobada_sf'
    )


def encolar_validacion_rechazada_sf(solicitud, validador, motivo, enlace_corregir=None, site_url=None):
    """
    Notifica al SOLICITANTE que su solicitud de fondos fue RECHAZADA.
    Versión específica para SolicitudFondos.
    """
    site_url = site_url or 'http://localhost:8000'
    
    if not enlace_corregir:
        enlace_corregir = f"{site_url}/solicitudes-fondos/{solicitud.id}/corregir"
    
    codigo = solicitud.numeroFormulario or f"SF-{solicitud.id}"
    solicitante = solicitud.usuario
    nombre_validador = validador.get_full_name()
    
    contexto = {
        'tipo': 'solicitud_fondos',
        'entidad': solicitud,
        'solicitud': solicitud,
        'solicitante': solicitante,
        'validador': validador,
        'nombre_validador': nombre_validador,
        'codigo': codigo,
        'monto': solicitud.montoSolicitado,
        'motivo': motivo,
        'enlace_corregir': enlace_corregir,
        'site_url': site_url,
        'fecha': timezone.now(),
        'icono': '❌',
        'titulo': 'Solicitud Rechazada',
        'color': '#f44336'
    }
    
    return encolar_email(
        destinatario=solicitante.email if hasattr(solicitante, 'email') else solicitante.correo,
        asunto=f"❌ Solicitud RECHAZADA - {codigo}",
        template_html='emails/validacion/rechazada_sf.html',
        contexto=contexto,
        prioridad=4,
        tipo_entidad='solicitud_fondos',
        entidad_id=solicitud.id,
        evento='validacion_rechazada_sf'
    )

# ============================================================
# FUNCIÓN PARA REVISIÓN DE SOLICITUD RECHAZADA
# ============================================================

def encolar_revision_solicitud_fondos(solicitud, validador, version, enlace_ver_detalle=None, site_url=None):
    """
    Notifica al VALIDADOR que una solicitud de fondos PREVIAMENTE RECHAZADA
    ha sido corregida y requiere una NUEVA REVISIÓN.
    
    Args:
        solicitud: Objeto SolicitudFondos
        validador: Objeto Usuario (el validador que debe revisar)
        version: String con la nueva versión (ej: "2")
        enlace_ver_detalle: URL para ver el detalle
        site_url: URL base del sitio
    """
    site_url = site_url or 'http://localhost:8000'
    
    if not enlace_ver_detalle:
        enlace_ver_detalle = f"{site_url}/solicitudes-fondos/{solicitud.id}/validar"
    
    codigo = solicitud.numeroFormulario or f"SF-{solicitud.id}"
    solicitante_nombre = solicitud.usuario.get_full_name() if solicitud.usuario else "Sistema"
    
    contexto = {
        'tipo': 'solicitud_fondos',
        'entidad': solicitud,
        'solicitud': solicitud,
        'validador': validador,
        'codigo': codigo,
        'monto': solicitud.montoSolicitado,
        'version': version,
        'solicitante_nombre': solicitante_nombre,
        'enlace_ver_detalle': enlace_ver_detalle,
        'site_url': site_url,
        'fecha': timezone.now(),
        'icono': '📝',
        'titulo': 'Nueva Revisión - Solicitud Corregida',
        'color': '#FF9800',
        'es_revision': True
    }
    
    return encolar_email(
        destinatario=validador.email if hasattr(validador, 'email') else validador.correo,
        asunto=f"📝 Nueva Revisión - {codigo} (v{version})",
        template_html='emails/validacion/revision_sf.html',
        contexto=contexto,
        prioridad=3,
        tipo_entidad='solicitud_fondos',
        entidad_id=solicitud.id,
        evento='revision_solicitud_fondos'
    )