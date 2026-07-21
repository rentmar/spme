# spme_mensajes/services/notificacion_service.py
from spme_mensajes.models import (
    MensajeUsuario,
    TipoMensaje,
    EstadoMensaje
)
from django.utils import timezone
import logging
from spme_actividades.models import TareaActividad
from typing import List
from spme_autenticacion.models import Usuario


logger = logging.getLogger(__name__)

def crear_mensaje_validacion_informe(informe_creado, validador):
    """
    Crea un registro de mensaje para la validación de un informe.
    Diseñado para ejecutarse DENTRO de una transacción existente.
    
    Args:
        informe_creado: Objeto InformeActividadPrincipal 
                        (con atributos: numeroInforme, id, usuario, etc.)
        validador: Dict con datos del validador
            {
                "id": 68,
                "nombre_completo": "Mark Rolqueza Bernal",
                "rol": "coordinador",
                "estado": "PENDIENTE",
                "fechaAsignacion": "2026-05-20T19:58:54.221Z"
            }
    
    Returns:
        MensajeUsuario creado o None si hay error
    """
    try:
        # Obtener datos del informe de forma segura
        numero_informe = getattr(informe_creado, 'numeroInforme', f'INF-{informe_creado.id}')
        actividad_id = getattr(informe_creado, 'actividad_id', None)
        proyecto_id = getattr(informe_creado, 'proyecto_id', None)
        
        # Nombre del elaborador
        if hasattr(informe_creado, 'usuario') and informe_creado.usuario:
            elaborado_por = informe_creado.usuario.get_full_name()
        else:
            elaborado_por = 'Sistema'
        
        # Fecha del informe
        if hasattr(informe_creado, 'fecha_creacion'):
            fecha_informe = informe_creado.fecha_creacion.strftime('%Y-%m-%d %H:%M')
        else:
            fecha_informe = timezone.now().strftime('%Y-%m-%d %H:%M')
        
        # Construir contenido del mensaje
        contenido = (
            f"Hola {validador['nombre_completo']},\n\n"
            f"Se requiere tu validación como {validador['rol']} "
            f"para el siguiente informe:\n\n"
            f"📋 Número de Informe: {numero_informe}\n"
            f"👤 Elaborado por: {elaborado_por}\n"
            f"📅 Fecha del informe: {fecha_informe}\n"
            f"🏷️ Tu rol: {validador['rol']}\n"
            f"⏰ Asignado: {validador.get('fechaAsignacion', timezone.now().strftime('%Y-%m-%d'))}\n\n"
            f"Por favor, revisa y emite tu validación a la brevedad posible."
        )

        # Crear el registro en el modelo
        mensaje = MensajeUsuario.objects.create(
            # Destinatario
            destinatario_id=validador['id'],
            
            # Remitente (Sistema)
            remitente=None,

            # Contenido
            tipo=TipoMensaje.ALERTA,
            asunto=f"📋 Validar Informe {numero_informe}",
            contenido=contenido,

            # Estado y prioridad
            estado=EstadoMensaje.NO_LEIDO,
            prioridad=3,  # ALTA

            # Fechas
            fecha_envio=timezone.now(),
            
            # Relaciones (usar getattr para evitar errores)
            actividad_id=actividad_id,
            proyecto_id=proyecto_id,

            # UI
            icono='📋',
            accion_url=f'/informes/{numero_informe}/validar',
            accion_texto='Validar Informe',

            # Sistema
            routing_key='mensaje.usuario.actividad',
            referencia_id=f"INF-{informe_creado.id}",

            # Metadata adicional
            metadata={
                'informe_id': informe_creado.id,
                'informe_numero': numero_informe,
                'tipo': 'validacion_informe',
                'rol_validador': validador['rol'],
                'estado_validacion': validador.get('estado'),
                'fecha_asignacion': validador.get('fechaAsignacion', str(timezone.now()))
            }
        )

        logger.info(
            f"✅ Mensaje creado para validador {validador['id']} "
            f"({validador['nombre_completo']}) - ID: {mensaje.id}"
        )
            
        return mensaje

    except Exception as e:
        logger.error(
            f"❌ Error creando mensaje para validador {validador.get('id')}: {str(e)}"
        )
        return None
    
    
def crear_mensajes_validacion_informe(informe_creado, validadores):
    """
    Crea mensajes para todos los validadores de un informe.
    
    Args:
        informe_creado: Objeto InformeActividadPrincipal
        validadores: Lista de dicts con datos de validadores
    
    Returns:
        Dict con resultados
    """
    resultados = {
        'creados': 0,
        'errores': 0,
        'mensajes': []
    }
    
    if not validadores:
        logger.info("No hay validadores para notificar")
        return resultados
    
    for validador in validadores:
        mensaje = crear_mensaje_validacion_informe(informe_creado, validador)
        
        if mensaje:
            resultados['creados'] += 1
            resultados['mensajes'].append({
                'validador_id': validador['id'],
                'nombre': validador.get('nombre_completo'),
                'rol': validador.get('rol'),
                'mensaje_id': mensaje.id,
                'message_id': mensaje.message_id
            })
        else:
            resultados['errores'] += 1
            resultados['mensajes'].append({
                'validador_id': validador['id'],
                'nombre': validador.get('nombre_completo'),
                'error': 'No se pudo crear el mensaje'
            })
    
    return resultados


def crear_mensaje_validacion_informe_tarea(informe_creado, validador):
    """
    Crea un registro de mensaje para la validacion de un informe
    Diseñado para ejecutarse dentro de una transaccion
    
    Args:
        informe_creado: Objeto InformeTareaPrincipal
                        (atributos: numeroInforme, id, usuario, etc)
    
        validador: Dict con datos del validador
            {
                "id": 68,
                "nombre_completo": "Mark Rolqueza Bernal",
                "rol": "coordinador",
                "estado": "PENDIENTE",
                "fechaAsignacion": "2026-05-20T19:58:54.221Z"
            }
    
    Returns:
        MensajeUsuario creado o None si hay Error
    """
    try:
        #obtener datos del informe de forma segura
        numero_informe = getattr(informe_creado, 'numeroInforme')
        tarea_id = getattr(informe_creado, 'tarea')
        #Cargar el objeto tarea
        tarea = informe_creado.tarea
        #Cargar el objeto actividad
        actividad = tarea.actividad if tarea else None
        #Cargar el proyecto
        proyecto = actividad.proyecto if actividad else None
        
        #Nombre del redactor
        if hasattr(informe_creado, 'usuario') and informe_creado.usuario:
            elaborado_por = informe_creado.usuario.get_full_name()
        else:
            elaborado_por = 'Sistema'
        
        # Fecha del informe
        if hasattr(informe_creado, 'fecha_creacion'):
            fecha_informe = informe_creado.fecha_creacion.strftime('%Y-%m-%d %H:%M')
        else:
            fecha_informe = timezone.now().strftime('%Y-%m-%d %H:%M')
        
        # Construir contenido del mensaje
        contenido = (
            f"Hola {validador['nombre_completo']},\n\n"
            f"Se requiere tu validación como {validador['rol']} "
            f"para el siguiente informe:\n\n"
            f"📋 Número de Informe: {numero_informe}\n"
            f"👤 Elaborado por: {elaborado_por}\n"
            f"📅 Fecha del informe: {fecha_informe}\n"
            f"🏷️ Tu rol: {validador['rol']}\n"
            f"⏰ Asignado: {validador.get('fechaAsignacion', timezone.now().strftime('%Y-%m-%d'))}\n\n"
            f"Por favor, revisa y emite tu validación a la brevedad posible."
        )

        #Crear el registro en el modelo
        mensaje = MensajeUsuario.objects.create(
            #Destinatario
            destinatario_id=validador['id'],
            # Remitente (Sistema)
            remitente=None,
            # Contenido
            tipo=TipoMensaje.ALERTA,
            asunto=f"📋 Validar Informe {numero_informe}",
            contenido=contenido,
            # Estado y prioridad
            estado=EstadoMensaje.NO_LEIDO,
            prioridad=3,  # ALTA
            # Fechas
            fecha_envio=timezone.now(),
            # Relaciones (usar getattr para evitar errores)
            actividad_id=actividad.id,
            proyecto_id=proyecto.id,
            # UI
            icono='📋',
            accion_url=f'/informes/{numero_informe}/validar',
            accion_texto='Validar Informe',
            # Sistema
            routing_key='mensaje.usuario.actividad',
            referencia_id=f"INF-{informe_creado.id}",
            # Metadata adicional
            metadata={
                'informe_id': informe_creado.id,
                'informe_numero': numero_informe,
                'tipo': 'validacion_informe',
                'rol_validador': validador['rol'],
                'estado_validacion': validador.get('estado'),
                'fecha_asignacion': validador.get('fechaAsignacion', str(timezone.now()))
            }

        )

        logger.info(
            f"✅ Mensaje creado para validador {validador['id']} "
            f"({validador['nombre_completo']}) - ID: {mensaje.id}"
        )

        return mensaje
        
    except Exception as e:
        logger.error(
            f"❌ Error creando mensaje para validador {validador.get('id')}: {str(e)}"
        )
        return None
    

def crear_mensajes_validacion_informe_tarea(informe_creado, validadores):
    """
    Crea mensajes para todos los validadores de un informe.
    
    Args:
        informe_creado: Objeto InformeTareaPrincipal
        validadores: Lista de dicts con datos de validadores
    
    Returns:
        Dict con resultados
    """
    resultados = {
        'creados': 0,
        'errores': 0,
        'mensajes': []
    }
    if not validadores:
        logger.info("No hay validadores para notificar")
        return resultados
    
    for validador in validadores:
        mensaje = crear_mensaje_validacion_informe_tarea(informe_creado, validador)
        if mensaje:
            resultados['creados'] += 1
            resultados['mensajes'].append({
                'validador_id': validador['id'],
                'nombre': validador.get('nombre_completo'),
                'rol': validador.get('rol'),
                'mensaje_id': mensaje.id,
                'message_id': mensaje.message_id
            })
        else:
            resultados['errores'] += 1
            resultados['mensajes'].append({
                'validador_id': validador['id'],
                'nombre': validador.get('nombre_completo'),
                'error': 'No se pudo crear el mensaje'
            })
    
    return resultados

# ===================================================================
# NOTIFICACIONES PARA SOLICITUD DE FONDOS
# ===================================================================

def crear_mensaje_validacion_solicitud_fondos(solicitud, validador):
    """
    Crea una notificación para el VALIDADOR cuando se le asigna
    una solicitud de fondos pendiente.
    
    Args:
        solicitud: Objeto SolicitudFondos
        validador: Dict con datos del validador
            {
                "id": 68,
                "nombre_completo": "Juan Pérez",
                "rol": "coordinador",
                "estado": "PENDIENTE",
                "fechaAsignacion": "2026-06-27T10:00:00Z"
            }
    
    Returns:
        MensajeUsuario creado o None si hay error
    """
    try:
        codigo = solicitud.numeroFormulario or f"SF-{solicitud.id}"
        monto = solicitud.montoSolicitado
        context = solicitud.get_mensaje_contexto()

        
        # ─── Determinar tipo (Actividad o Tarea) ───
        if solicitud.actividad_id and not solicitud.tarea_id:
            tipo_solicitud = "Actividad"
            actividad_nombre = getattr(solicitud.actividad, 'nombreCorto', str(solicitud.actividad))
            detalle = f"📋 Actividad: {actividad_nombre}\n"
            
        elif solicitud.actividad_id and solicitud.tarea_id:
            tipo_solicitud = "Tarea"
            actividad_nombre = getattr(
                getattr(solicitud.tarea, 'actividad', None), 'nombreCorto', 'N/A'
            )
            tarea_nombre = getattr(solicitud.tarea, 'descripcionTarea', str(solicitud.tarea))
            detalle = f"📋 Actividad: {actividad_nombre}\n📎 Tarea: {tarea_nombre}\n"
            
        else:
            tipo_solicitud = "General"
            detalle = ""
        
        # ─── Datos del solicitante ───
        solicitante_nombre = (
            solicitud.usuario.get_full_name() 
            if solicitud.usuario 
            else "Sistema"
        )
        
        # ─── Fecha formateada ───
        fecha_solicitud = (
            solicitud.fechaSolicitud.strftime('%Y-%m-%d')
            if solicitud.fechaSolicitud
            else timezone.now().strftime('%Y-%m-%d')
        )
        
        # ─── Contenido del mensaje ───
        contenido = (
            f"Hola {validador['nombre_completo']},\n\n"
            f"Se requiere tu validación como {validador['rol']} "
            f"para la siguiente solicitud de fondos:\n\n"
            f"💵 Código: {codigo}\n"
            f"💰 Monto: ${monto:,.2f}\n"
            f"📌 Tipo: Solicitud para {tipo_solicitud}\n"
            f"{detalle}"
            f"👤 Solicitante: {solicitante_nombre}\n"
            f"📅 Fecha: {fecha_solicitud}\n"
            f"🏷️ Tu rol: {validador['rol']}\n"
            f"⏰ Asignado: {validador.get('fechaAsignacion', timezone.now().strftime('%Y-%m-%d'))}\n\n"
            f"Por favor, revisa y emite tu validación a la brevedad posible."
        )
        
        # ─── IDs de relaciones ───
        actividad_id = solicitud.actividad_id
        proyecto_id = (
            solicitud.actividad.proyecto_id
            if solicitud.actividad and hasattr(solicitud.actividad, 'proyecto_id')
            else None
        )
        
        # ─── Crear el mensaje ───
        mensaje = MensajeUsuario.objects.create(
            destinatario_id=validador['id'],
            remitente=None,
            tipo=TipoMensaje.ALERTA,
            asunto=f"💵 Validar Solicitud de Fondos - {codigo}",
            contenido=contenido,
            estado=EstadoMensaje.NO_LEIDO,
            prioridad=3,
            fecha_envio=timezone.now(),
            actividad_id=actividad_id,
            proyecto_id=proyecto_id,
            icono='💵',
            accion_url=context['accion_url'],
            accion_texto=context['accion_url_texto'],
            routing_key='mensaje.usuario.solicitud_fondos',
            referencia_id=f"SF-{solicitud.id}",
            metadata={
                'solicitud_id': solicitud.id,
                'solicitud_codigo': codigo,
                'monto': str(monto),
                'tipo_solicitud': tipo_solicitud,
                'tipo': 'validacion_solicitud_fondos',
                'rol_validador': validador['rol'],
            }
        )
        
        logger.info(
            f"✅ Mensaje creado para validador {validador['id']} "
            f"({validador['nombre_completo']}) - ID: {mensaje.id}"
        )
        return mensaje
        
    except Exception as e:
        logger.error(f"❌ Error creando mensaje: {e}")
        #return None
        raise


def crear_mensajes_validacion_solicitud_fondos(solicitud, validadores):
    """
    Crea notificaciones para TODOS los validadores de una solicitud.
    
    Args:
        solicitud: Objeto SolicitudFondos
        validadores: Lista de dicts con datos de validadores
    
    Returns:
        Dict con resultados {creados, errores, mensajes}
    """
    resultados = {
        'creados': 0,
        'errores': 0,
        'mensajes': []
    }
    
    if not validadores:
        logger.info("No hay validadores para notificar")
        return resultados
    
    for validador in validadores:
        mensaje = crear_mensaje_validacion_solicitud_fondos(solicitud, validador)
        
        if mensaje:
            resultados['creados'] += 1
            resultados['mensajes'].append({
                'validador_id': validador['id'],
                'nombre': validador.get('nombre_completo'),
                'rol': validador.get('rol'),
                'mensaje_id': mensaje.id
            })
        else:
            resultados['errores'] += 1
            resultados['mensajes'].append({
                'validador_id': validador['id'],
                'nombre': validador.get('nombre_completo'),
                'error': 'No se pudo crear el mensaje'
            })
    
    logger.info(
        f"📊 Lote procesado: {resultados['creados']} creados, "
        f"{resultados['errores']} errores de {len(validadores)}"
    )
    return resultados


def crear_mensaje_solicitud_aprobada(solicitud, validaciones_aprobadas):
    """
    Notifica al SOLICITANTE que su solicitud fue APROBADA.
    Se ejecuta cuando TODOS los validadores aprobaron.
    
    Args:
        solicitud: Objeto SolicitudFondos
        validaciones_aprobadas: Lista/QuerySet de ValidacionSolicitudFondos
    
    Returns:
        MensajeUsuario creado o None
    """
    try:
        if not solicitud.usuario:
            logger.error("❌ La solicitud no tiene usuario asociado")
            return None
        
        codigo = solicitud.numeroFormulario or f"SF-{solicitud.id}"
        monto = solicitud.montoSolicitado
        total = len(validaciones_aprobadas)
        context = solicitud.get_mensaje_contexto()
        
        # ─── Construir resumen de validadores ───
        resumen = ""
        for v in validaciones_aprobadas:
            nombre = v.usuarioValidador.get_full_name()
            fecha = (
                v.fechaResolucion.strftime('%Y-%m-%d %H:%M')
                if v.fechaResolucion else 'N/A'
            )
            comentario = v.comentarios or 'Sin comentarios'
            resumen += (
                f"✅ {nombre}\n"
                f"   Fecha: {fecha}\n"
                f"   Comentario: {comentario}\n\n"
            )
        
        # ─── Contenido del mensaje ───
        contenido = (
            f"Hola {solicitud.usuario.get_full_name()},\n\n"
            f"¡Buenas noticias! Tu solicitud de fondos ha sido "
            f"APROBADA por todos los validadores.\n\n"
            f"💵 Código: {codigo}\n"
            f"💰 Monto: ${monto:,.2f}\n"
            f"📅 Fecha de aprobación: {timezone.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            f"📊 Resultado de Validación ({total}/{total}):\n\n"
            f"{resumen}"
            f"La solicitud ha sido aprobada y puede proceder con su ejecución."
        )
        
        # ─── IDs de relaciones ───
        actividad_id = solicitud.actividad_id
        proyecto_id = (
            solicitud.actividad.proyecto_id
            if solicitud.actividad and hasattr(solicitud.actividad, 'proyecto_id')
            else None
        )
        
        # ─── Crear mensaje ───
        mensaje = MensajeUsuario.objects.create(
            destinatario=solicitud.usuario,
            remitente=None,
            tipo=TipoMensaje.ALERTA,
            asunto=f"✅ Solicitud APROBADA - {codigo}",
            contenido=contenido,
            estado=EstadoMensaje.NO_LEIDO,
            prioridad=3,
            fecha_envio=timezone.now(),
            actividad_id=actividad_id,
            proyecto_id=proyecto_id,
            icono='✅',
            accion_url=context['accion_url'],
            accion_texto=context['accion_url_texto'],
            routing_key='mensaje.usuario.solicitud_fondos',
            referencia_id=f"SF-{solicitud.id}",
            metadata={
                'solicitud_id': solicitud.id,
                'solicitud_codigo': codigo,
                'monto': str(monto),
                'tipo': 'solicitud_aprobada',
                'total_validadores': total,
                'fecha_aprobacion': str(timezone.now())
            }
        )
        
        logger.info(
            f"✅ Mensaje de APROBACIÓN para {solicitud.usuario.get_full_name()} "
            f"- {codigo} - ID: {mensaje.id}"
        )
        return mensaje
        
    except Exception as e:
        logger.error(f"❌ Error: {type(e).__name__}: {e}")
        logger.error(f"❌ Traceback:", exc_info=True)
        logger.error(f"❌ Error en mensaje de aprobación: {e}")
        return None
    


def crear_mensaje_solicitud_rechazada(solicitud, validador_que_rechazo, motivo):
    """
    Notifica al SOLICITANTE que su solicitud fue RECHAZADA.
    Se ejecuta INMEDIATAMENTE cuando un validador rechaza.
    
    Args:
        solicitud: Objeto SolicitudFondos
        validador_que_rechazo: Objeto Usuario (quién rechazó)
        motivo: String con el motivo del rechazo
    
    Returns:
        MensajeUsuario creado o None
    """
    try:
        if not solicitud.usuario:
            logger.error("❌ La solicitud no tiene usuario asociado")
            return None
        
        codigo = solicitud.numeroFormulario or f"SF-{solicitud.id}"
        monto = solicitud.montoSolicitado
        nombre_validador = validador_que_rechazo.get_full_name()
        contexto = solicitud.get_mensaje_contexto()
        
        # ─── Contenido del mensaje ───
        contenido = (
            f"Hola {solicitud.usuario.get_full_name()},\n\n"
            f"Tu solicitud de fondos ha sido RECHAZADA.\n\n"
            f"💵 Código: {codigo}\n"
            f"💰 Monto: ${monto:,.2f}\n"
            f"📅 Fecha de rechazo: {timezone.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            f"❌ Rechazado por: {nombre_validador}\n"
            f"📝 Motivo del rechazo:\n"
            f"{motivo}\n\n"
            f"Puedes corregir la solicitud y reenviarla para una nueva validación."
        )
        
        # ─── IDs de relaciones ───
        actividad_id = solicitud.actividad_id
        proyecto_id = (
            solicitud.actividad.proyecto_id
            if solicitud.actividad and hasattr(solicitud.actividad, 'proyecto_id')
            else None
        )
        
        # ─── Crear mensaje ───
        mensaje = MensajeUsuario.objects.create(
            destinatario=solicitud.usuario,
            remitente=None,
            tipo=TipoMensaje.ALERTA,
            asunto=f"❌ Solicitud RECHAZADA - {codigo}",
            contenido=contenido,
            estado=EstadoMensaje.NO_LEIDO,
            prioridad=3,
            fecha_envio=timezone.now(),
            actividad_id=actividad_id,
            proyecto_id=proyecto_id,
            icono='❌',
            accion_url=contexto['accion_url'],
            accion_texto=contexto['accion_url_texto'],
            routing_key='mensaje.usuario.solicitud_fondos',
            referencia_id=f"SF-{solicitud.id}",
            metadata={
                'solicitud_id': solicitud.id,
                'solicitud_codigo': codigo,
                'monto': str(monto),
                'tipo': 'solicitud_rechazada',
                'validador_id': validador_que_rechazo.id,
                'validador_nombre': nombre_validador,
                'motivo': motivo,
                'fecha_rechazo': str(timezone.now())
            }
        )
        
        logger.info(
            f"✅ Mensaje de RECHAZO para {solicitud.usuario.get_full_name()} "
            f"- {codigo} - Validador: {nombre_validador} - ID: {mensaje.id}"
        )
        return mensaje
        
    except Exception as e:
        logger.error(f"❌ Error en mensaje de rechazo: {e}")
        return None
    
def crear_mensaje_revision_solicitud_fondos(solicitud, validador, version):
    """
    Mensaje interno notificando que un documento RECHAZADO ha sido corregido
    y requiere una NUEVA REVISIÓN.
    """
    try:
        codigo = solicitud.numeroFormulario or f"SF-{solicitud.id}"
        monto = solicitud.montoSolicitado
        solicitante_nombre = solicitud.usuario.get_full_name() if solicitud.usuario else "Sistema"
        contexto = solicitud.get_mensaje_contexto()

        contenido = (
            f"Hola {validador['nombre_completo']},\n\n"
            f"📝 NUEVA REVISIÓN SOLICITADA\n\n"
            f"El documento que fue previamente rechazado ha sido CORREGIDO "
            f"y requiere una nueva revisión.\n\n"
            f"💵 Solicitud: {codigo}\n"
            f"💰 Monto: ${monto:,.2f}\n"
            f"📌 Versión: {version}\n"
            f"👤 Solicitante: {solicitante_nombre}\n"
            f"⏰ Asignado: {validador.get('fechaAsignacion', timezone.now().strftime('%Y-%m-%d'))}\n\n"
            f"Por favor, revisa la nueva versión del documento y emite tu validación."
        )
        
        mensaje = MensajeUsuario.objects.create(
            destinatario_id=validador['id'],
            remitente=None,
            tipo=TipoMensaje.ALERTA,
            asunto=f"📝 Nueva Revisión - {codigo} (v{version})",
            contenido=contenido,
            estado=EstadoMensaje.NO_LEIDO,
            prioridad=3,
            fecha_envio=timezone.now(),
            icono='📝',
            accion_url=contexto['accion_url'],
            accion_texto=contexto['accion_url_texto'],
            routing_key='mensaje.usuario.solicitud_fondos',
            referencia_id=f"SF-{solicitud.id}",
            metadata={
                'solicitud_id': solicitud.id,
                'solicitud_codigo': codigo,
                'tipo': 'nueva_revision',
                'version': version
            }
        )
        
        logger.info(f"✅ Mensaje de REVISIÓN creado - {codigo} v{version} - ID: {mensaje.id}")
        return mensaje
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return None


# =========================================================================================
#        NOTIFICACIONES PARA FORMULARIOS
# =========================================================================================
TIPO_NOMBRE_MAP = {
    'fondos': 'Solicitud de Fondos',
    'reposicion': 'Solicitud de Reposición',
    'viaje': 'Solicitud de Viaje',
    'pago_directo': 'Pago Directo',
    'rendicion': 'Rendición de Cuentas',
}

ICONO_MAP = {
    'fondos': '💵',
    'reposicion': '💳',
    'viaje': '✈️',
    'pago_directo': '💳',
    'rendicion': '📋',
}
def enviar_notificacion_mensajeria_interna(tipo:str, accion:str, solicitud, destinatarios_ids: List[int], base_url: str, motivo: str = '',version: str = '1',)->dict: 
    """
    Orquestador de notificaciones internas.
    Args:
        solicitud: Objeto de la solicitud
        destinatarios_ids: [68, 46]
        base_url: URL base del frontend
        tipo: 'fondos' | 'reposicion' | 'viaje' | 'pago_directo' | 'rendicion'
        accion: 'revision' | 'aprobacion' | 'rechazo' | 'nueva_revision'
        motivo: Texto del rechazo
        version: Versión del documento
    Returns:
        dict: {'mensajes': [MensajeUsuario, ...]}
    """
    #Comprobar si el tipo de documento se encuentra soportado
    if tipo not in TIPO_NOMBRE_MAP:
        raise ValueError(f"Tipo de documento no soportado: {tipo}")
    
    acciones = {
        'revision': lambda: _procesar_revision(
            solicitud=solicitud,
            revisores_ids=destinatarios_ids,
            tipo=tipo,
            base_url=base_url,
        ),
        'aprobacion': lambda: _procesar_aprobacion(
            solicitud=solicitud,
            redactores_ids=destinatarios_ids,
            tipo=tipo,
            base_url=base_url,
        ),
        'rechazo': lambda: _procesar_rechazo(
            solicitud=solicitud,
            redactores_ids=destinatarios_ids,
            tipo=tipo,
            motivo=motivo,
            base_url=base_url,
        ),
        'nueva_revision': lambda: _procesar_nueva_revision(
            solicitud=solicitud,
            destinatarios_ids=destinatarios_ids,
            tipo=tipo,
            version=version,
            base_url=base_url,
        ),
    }

    if accion not in acciones:
        raise ValueError(f"Acción no soportada: {accion}")
    
    return acciones[accion]()

#Funcion para procesar peticion de revision
def _procesar_revision(tipo, solicitud, revisores_ids, base_url):
    """
    Procesa por lotes de mensajes
    Args:
        tipo: 'fondos' | 'reposicion' | 'viaje' | 'pago_directo' | 'rendicion'
        solicitud: Objeto de la solicitud
        revisores_ids: [68, 46]
        base_url: URL base del frontend
    Returns:
        dict: {'mensajes': [MensajeUsuario, ...]}

    """
    resultados = {
        'creados': 0,
        'errores': 0,
        'mensajes': []
    }
    #Comprobar si hay revisores
    if not revisores_ids:
        logger.info("No hay revisores para notificar")
        return resultados
    
    #Crear mensaje
    for revisor in revisores_ids:
        mensaje = _crear_mensaje_peticion_revision(tipo, solicitud, revisor)
        if mensaje:
            resultados['creados'] += 1
            resultados['mensajes'].append({
                'validador_id': revisor,
                'mensaje_id': mensaje.id
            })
        else:
            resultados['errores'] += 1
            resultados['mensajes'].append({
                'validador_id': revisor,
                'error': 'No se pudo crear el mensaje'
            })
    
    logger.info(
            f"📊 Lote procesado: {resultados['creados']} creados, "
            f"{resultados['errores']} errores"
        )
    return resultados

#Funcion para procesaro aprobacion
def _procesar_aprobacion(tipo, solicitud, redactores_ids, base_url):
    """
    Procesa por lotes de mensajes
    Args:
        tipo: 'fondos' | 'reposicion' | 'viaje' | 'pago_directo' | 'rendicion'
        solicitud: Objeto de la solicitud
        revisores_ids: [68, 46]
        base_url: URL base del frontend
    Returns:
        dict: {'mensajes': [MensajeUsuario, ...]}

    """
    resultados = {
        'creados': 0,
        'errores': 0,
        'mensajes': []
    }

    #Comprobar si hay revisores
    if not redactores_ids:
        logger.info("No hay redactores para notificar")
        return resultados
    
    #Crear mensaje
    for revisor in redactores_ids:
        mensaje = _crear_mensaje_aprobacion(tipo, solicitud, revisor)
        if mensaje:
            resultados['creados'] += 1
            resultados['mensajes'].append({
                'validador_id': revisor,
                'mensaje_id': mensaje.id
            })
        else:
            resultados['errores'] += 1
            resultados['mensajes'].append({
                'validador_id': revisor,
                'error': 'No se pudo crear el mensaje'
            })
    
    logger.info(
            f"📊 Lote procesado: {resultados['creados']} creados, "
            f"{resultados['errores']} errores"
        )
    return resultados
    
#Funcion para procesar rechazo
def _procesar_rechazo(tipo, solicitud, redactores_ids, base_url, motivo):
    """
    Procesa por lotes de mensajes
    Args:
        tipo: 'fondos' | 'reposicion' | 'viaje' | 'pago_directo' | 'rendicion'
        solicitud: Objeto de la solicitud
        revisores_ids: [68, 46]
        base_url: URL base del frontend
    Returns:
        dict: {'mensajes': [MensajeUsuario, ...]}
    """
    resultados = {
        'creados': 0,
        'errores': 0,
        'mensajes': []
    }
    #Comprobar si hay revisores
    if not redactores_ids:
        logger.info("No hay redactores para notificar")
        return resultados
    
    #Crear mensaje
    for revisor in redactores_ids:
        mensaje = _crear_mensaje_rechazo(tipo, solicitud, revisor, comentario=motivo)
        if mensaje:
            resultados['creados'] += 1
            resultados['mensajes'].append({
                'validador_id': revisor,
                'mensaje_id': mensaje.id
            })
        else:
            resultados['errores'] += 1
            resultados['mensajes'].append({
                'validador_id': revisor,
                'error': 'No se pudo crear el mensaje'
            })
    
    logger.info(
            f"📊 Lote procesado: {resultados['creados']} creados, "
            f"{resultados['errores']} errores"
        )
    return resultados
    


    

#Funcion para procesar nueva revision
def _procesar_nueva_revision(tipo, solicitud, destinatarios_ids, base_url, version):

    """
    Procesa por lotes de mensajes
    Args:
        tipo: 'fondos' | 'reposicion' | 'viaje' | 'pago_directo' | 'rendicion'
        solicitud: Objeto de la solicitud
        revisores_ids: [68, 46]
        base_url: URL base del frontend
    Returns:
        dict: {'mensajes': [MensajeUsuario, ...]}

    """
    resultados = {
        'creados': 0,
        'errores': 0,
        'mensajes': []
    }
    #Comprobar si hay revisores
    if not destinatarios_ids:
        logger.info("No hay revisores para notificar")
        return resultados
    
    #Crear mensaje
    for revisor in destinatarios_ids:
        mensaje = _crear_mensaje_nueva_revision(tipo, solicitud, revisor, version)
        if mensaje:
            resultados['creados'] += 1
            resultados['mensajes'].append({
                'validador_id': revisor,
                'mensaje_id': mensaje.id
            })
        else:
            resultados['errores'] += 1
            resultados['mensajes'].append({
                'validador_id': revisor,
                'error': 'No se pudo crear el mensaje'
            })
    
    logger.info(
            f"📊 Lote procesado: {resultados['creados']} creados, "
            f"{resultados['errores']} errores"
        )
    return resultados


#Funcion para crear mensaje para petcion de revision
def _crear_mensaje_peticion_revision(tipo, solicitud, revisor_id):
    """
    Crear una notificacion para informar a los revisores que una solicitud
    se les asigno y requiere su revision
    Args:
        tipo_display: String para el tipo de documento
        solicitud: Objeto SolicitudFondos
        revisor_id: Revisor ID
    
    Returns:
        MensajeUsuario creado o None si hay error
    """
    try:
        tipo_icono = ICONO_MAP[tipo]
        tipo_nombre = TIPO_NOMBRE_MAP[tipo]
        codigo = solicitud.numeroFormulario
        monto = solicitud.montoSolicitado
        context = solicitud.get_mensaje_contexto()
        revisor = Usuario.objects.get(id=revisor_id)
        validacion = _extraer_validacion_por_revisor(solicitud, tipo, revisor_id)

        # print('TIPO: ', tipo_nombre)
        # print('CONTEXTO: ', context)
        # print('VALIDACION: ', validacion)

        #Determinar el subtipo del documento
        if solicitud.actividad_id and not solicitud.tarea_id:
            tipo_solicitud = "Actividad"
            actividad_nombre = getattr(solicitud.actividad, 'nombreCorto', str(solicitud.actividad))
            detalle = f"📋 Actividad: {actividad_nombre}\n"
            
        elif solicitud.actividad_id and solicitud.tarea_id:
            tipo_solicitud = "Tarea"
            actividad_nombre = getattr(
                getattr(solicitud.tarea, 'actividad', None), 'nombreCorto', 'N/A'
            )
            tarea_nombre = getattr(solicitud.tarea, 'descripcionTarea', str(solicitud.tarea))
            detalle = f"📋 Actividad: {actividad_nombre}\n📎 Tarea: {tarea_nombre}\n"
            
        else:
            tipo_solicitud = "General"
            detalle = ""
        
        print('SUBTIPO: ', tipo_solicitud)

        #NOmbre del solicitante
        solicitante_nombre = context['solicitante_nombre']

        #Revisor
        revisor_nombre = revisor.get_full_name()
        print('Revisor: ', revisor_nombre)
        #Fecha de la solicitud
        fecha_solicitud = (
            solicitud.fechaSolicitud.strftime('%Y-%m-%d')
            if solicitud.fechaSolicitud
            else timezone.now().strftime('%Y-%m-%d')
        )

        #Contenido del mensaje
        contenido = (
            f"Hola {revisor.get_full_name()},\n\n"
            f"Se requiere tu validación como {revisor.cargo} "
            f"para la siguiente { tipo_icono } {tipo_nombre}:\n\n"
            f"💵 Código: {codigo}\n"
            f"💰 Monto: ${monto:,.2f}\n"
            f"📌 Tipo: Solicitud para {tipo_solicitud}\n"
            f"{detalle}"
            f"👤 Solicitante: {solicitante_nombre}\n"
            f"📅 Fecha: {fecha_solicitud}\n"
            f"🏷️ Tu rol: {revisor.cargo}\n"
            f"⏰ Asignado: {validacion['fechaAsignacion'] }\n\n"
            f"Por favor, revisa y emite tu validación a la brevedad posible."
        )

        #Genera el mensaje
        mensaje = MensajeUsuario.objects.create(
            destinatario_id = revisor_id,
            remitente=None,
            tipo=TipoMensaje.ALERTA,
            asunto=f"📝 Revisión - {codigo} (v{validacion['versionDocumento']})",
            contenido=contenido,
            estado=EstadoMensaje.NO_LEIDO,
            prioridad=3,
            fecha_envio=timezone.now(),
            icono='📝',
            accion_url=context['accion_url'],
            accion_texto=context['accion_url_texto'],
            routing_key='mensaje.usuario.solicitud_viaje',
            referencia_id=f"SV-{solicitud.id}",
            metadata={
                'solicitud_id': solicitud.id,
                'solicitud_codigo': codigo,
                'tipo': 'revision',
                'version': validacion['versionDocumento']
            }
        )

        logger.info(f"✅ Mensaje de REVISIÓN creado - {codigo} v{validacion['versionDocumento']} - ID: {mensaje.id}")
        return mensaje
    
    except Exception as e:
        logger.error(f"❌ Error creando mensaje: {e}")
        #return None
        raise


#Funcion para crear mensaje aprobacion
def _crear_mensaje_aprobacion(tipo, solicitud, revisor_id):
    """
    Crear una notificacion para informar al redactor que su solicitud ha sido aprobada
    Args:
        tipoy: String para el tipo de documento
        solicitud: Objeto SolicitudFondos
        revisor_id: Revisor ID
    
    Returns:
        MensajeUsuario creado o None si hay error
    """
    try:
        tipo_icono = ICONO_MAP[tipo]
        tipo_nombre = TIPO_NOMBRE_MAP[tipo]
        codigo = solicitud.numeroFormulario
        monto = solicitud.montoSolicitado
        context = solicitud.get_mensaje_contexto()
        redactor = Usuario.objects.get(id=revisor_id)

        #Determinar el subtipo del documento
        if solicitud.actividad_id and not solicitud.tarea_id:
            tipo_solicitud = "Actividad"
            actividad_nombre = getattr(solicitud.actividad, 'nombreCorto', str(solicitud.actividad))
            detalle = f"📋 Actividad: {actividad_nombre}\n"
            
        elif solicitud.actividad_id and solicitud.tarea_id:
            tipo_solicitud = "Tarea"
            actividad_nombre = getattr(
                getattr(solicitud.tarea, 'actividad', None), 'nombreCorto', 'N/A'
            )
            tarea_nombre = getattr(solicitud.tarea, 'descripcionTarea', str(solicitud.tarea))
            detalle = f"📋 Actividad: {actividad_nombre}\n📎 Tarea: {tarea_nombre}\n"
            
        else:
            tipo_solicitud = "General"
            detalle = ""
        
        print('SUBTIPO: ', tipo_solicitud)

        #NOmbre del solicitante
        solicitante_nombre = context['solicitante_nombre']

        #Fecha de la solicitud
        fecha_solicitud = (
            solicitud.fechaSolicitud.strftime('%Y-%m-%d')
            if solicitud.fechaSolicitud
            else timezone.now().strftime('%Y-%m-%d')
        )

        #Contenido del mensaje
        contenido = (
            f"Hola { redactor.get_full_name()},\n\n"
            f"Tu solicitud de {tipo_icono} {tipo_nombre} ha sido "
            f"APROBADA por todos los revisores.\n\n"
            f"💵 Código: {codigo}\n"
            f"💰 Monto: ${monto:,.2f}\n"
            f"📅 Fecha de aprobación: {timezone.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            f"La solicitud ha sido aprobada y puede proceder con su ejecución."
        )
        # ─── Crear mensaje ───
        mensaje = MensajeUsuario.objects.create(
            destinatario=solicitud.usuario,
            remitente=None,
            tipo=TipoMensaje.ALERTA,
            asunto=f"✅ Solicitud APROBADA - {codigo}",
            contenido=contenido,
            estado=EstadoMensaje.NO_LEIDO,
            prioridad=3,
            fecha_envio=timezone.now(),
            icono='✅',
            accion_url=context['accion_url'],
            accion_texto=context['accion_url_texto'],
            routing_key='mensaje.usuario.solicitud_fondos',
            referencia_id=f"SV-{solicitud.id}",
            metadata={
                'solicitud_id': solicitud.id,
                'solicitud_codigo': codigo,
                'monto': str(monto),
                'tipo': 'aprovacion',
            }
        )
        
        logger.info(
            f"✅ Mensaje de APROBACIÓN para {solicitud.usuario.get_full_name()} "
            f"- {codigo} - ID: {mensaje.id}"
        )
        return mensaje   
    except Exception as e:
        logger.error(f"❌ Error creando mensaje: {e}")
        #return None
        raise




#Funcion para crear mensaje de rechazo
def _crear_mensaje_rechazo(tipo, solicitud, redactor_id, comentario):
    """
    Crear una notificacion para informar al redactor que su solicitud ha sido rechazada
    Args:
        tipo: String para el tipo de documento
        solicitud: Objeto SolicitudFondos
        revisor_id: Revisor ID
    
    Returns:
        MensajeUsuario creado o None si hay error
    """

    try:
        tipo_icono = ICONO_MAP[tipo]
        tipo_nombre = TIPO_NOMBRE_MAP[tipo]
        codigo = solicitud.numeroFormulario
        monto = solicitud.montoSolicitado
        context = solicitud.get_mensaje_contexto()
        redactor = Usuario.objects.get(id=redactor_id)
        motivo = comentario

        #Determinar el subtipo del documento
        if solicitud.actividad_id and not solicitud.tarea_id:
            tipo_solicitud = "Actividad"
            actividad_nombre = getattr(solicitud.actividad, 'nombreCorto', str(solicitud.actividad))
            detalle = f"📋 Actividad: {actividad_nombre}\n"
            
        elif solicitud.actividad_id and solicitud.tarea_id:
            tipo_solicitud = "Tarea"
            actividad_nombre = getattr(
                getattr(solicitud.tarea, 'actividad', None), 'nombreCorto', 'N/A'
            )
            tarea_nombre = getattr(solicitud.tarea, 'descripcionTarea', str(solicitud.tarea))
            detalle = f"📋 Actividad: {actividad_nombre}\n📎 Tarea: {tarea_nombre}\n"
            
        else:
            tipo_solicitud = "General"
            detalle = ""

        contenido = (
            f"Hola {redactor.get_full_name()},\n\n"
            f"Tu  {tipo_icono} {tipo_nombre} ha sido RECHAZADA.\n\n"
            f"💵 Código: {codigo}\n"
            f"💰 Monto: ${monto:,.2f}\n"
            f"📅 Fecha de rechazo: {timezone.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            f"❌ Rechazado"
            f"📝 Motivo del rechazo:\n"
            f"{motivo}\n\n"
            f"Puedes corregir la solicitud y reenviarla para una nueva validación."
        )

        # ─── Crear mensaje ───
        mensaje = MensajeUsuario.objects.create(
            destinatario=redactor,
            remitente=None,
            tipo=TipoMensaje.ALERTA,
            asunto=f"❌ Solicitud Rechazada - {codigo}",
            contenido=contenido,
            estado=EstadoMensaje.NO_LEIDO,
            prioridad=3,
            fecha_envio=timezone.now(),
            icono='✅',
            accion_url=context['accion_url'],
            accion_texto=context['accion_url_texto'],
            routing_key='mensaje.usuario.solicitud_viaje',
            referencia_id=f"SV-{solicitud.id}",
            metadata={
                'solicitud_id': solicitud.id,
                'solicitud_codigo': codigo,
                'monto': str(monto),
                'tipo': 'rechazo',
            }
        )
        
        logger.info(
            f"❌ Mensaje de RECHAZO para {solicitud.usuario.get_full_name()} "
            f"- {codigo} - ID: {mensaje.id}"
        )
        return mensaje 

    except Exception as e:
        logger.error(f"❌ Error creando mensaje: {e}")
        #return None
        raise


#Funcion para crear mensaje para peticion de nueva revision
def _crear_mensaje_nueva_revision(tipo, solicitud, revisor_id, version):
    """
    Genera mensaje para nueva revision
    """
    try:
        tipo_icono = ICONO_MAP[tipo]
        tipo_nombre = TIPO_NOMBRE_MAP[tipo]
        codigo = solicitud.numeroFormulario
        monto = solicitud.montoSolicitado
        context = solicitud.get_mensaje_contexto()
        revisor = Usuario.objects.get(id=revisor_id)
        
        
        # print('TIPO: ', tipo_nombre)
        # print('CONTEXTO: ', context)
        # print('VALIDACION: ', validacion)

        #Determinar el subtipo del documento
        if solicitud.actividad_id and not solicitud.tarea_id:
            tipo_solicitud = "Actividad"
            actividad_nombre = getattr(solicitud.actividad, 'nombreCorto', str(solicitud.actividad))
            detalle = f"📋 Actividad: {actividad_nombre}\n"
            
        elif solicitud.actividad_id and solicitud.tarea_id:
            tipo_solicitud = "Tarea"
            actividad_nombre = getattr(
                getattr(solicitud.tarea, 'actividad', None), 'nombreCorto', 'N/A'
            )
            tarea_nombre = getattr(solicitud.tarea, 'descripcionTarea', str(solicitud.tarea))
            detalle = f"📋 Actividad: {actividad_nombre}\n📎 Tarea: {tarea_nombre}\n"
            
        else:
            tipo_solicitud = "General"
            detalle = ""
        
        print('SUBTIPO: ', tipo_solicitud)

        #NOmbre del solicitante
        solicitante_nombre = context['solicitante_nombre']

        #Revisor
        revisor_nombre = revisor.get_full_name()
        print('Revisor: ', revisor_nombre)
        #Fecha de la solicitud
        fecha_solicitud = (
            solicitud.fechaSolicitud.strftime('%Y-%m-%d')
            if solicitud.fechaSolicitud
            else timezone.now().strftime('%Y-%m-%d')
        )
        contenido = (
            f"Hola {revisor.get_full_name()},\n\n"
            f"📝 NUEVA REVISIÓN SOLICITADA\n\n"
            f"El documento que fue previamente rechazado ha sido CORREGIDO "
            f"y requiere una nueva revisión.\n\n"
            f"💵 Solicitud: {codigo}\n"
            f"💰 Monto: ${monto:,.2f}\n"
            f"📌 Versión: {version}\n"
            f"👤 Solicitante: {solicitante_nombre}\n"
            f"Por favor, revisa la nueva versión del documento y emite tu validación."
        )
        
        mensaje = MensajeUsuario.objects.create(
            destinatario_id=revisor.id,
            remitente=None,
            tipo=TipoMensaje.ALERTA,
            asunto=f"📝 Nueva Revisión - {codigo} (v{version})",
            contenido=contenido,
            estado=EstadoMensaje.NO_LEIDO,
            prioridad=3,
            fecha_envio=timezone.now(),
            icono='📝',
            accion_url=context['accion_url'],
            accion_texto=context['accion_url_texto'],
            routing_key='mensaje.usuario.solicitud_fondos',
            referencia_id=f"SF-{solicitud.id}",
            metadata={
                'solicitud_id': solicitud.id,
                'solicitud_codigo': codigo,
                'tipo': 'nueva_revision',
                'version': version
            }
        )
        
        logger.info(f"✅ Mensaje de REVISIÓN creado - {codigo} v{version} - ID: {mensaje.id}")
        return mensaje
        
    
    except Exception as e:
        logger.error(f"❌ Error creando mensaje: {e}")
        #return None
        raise




    

#Extraer validaciones por revisor
def _extraer_validacion_por_revisor(solicitud, tipo: str, revisor_id: int) -> dict:
    """
    Extrae la validación de un revisor específico.
    
    Returns:
        dict con los datos de la validación o None si no existe
    """
    from spme_validaciones.models import (
        ValidacionSolicitudFondos,
        ValidacionSolicitudReembolso,
        ValidacionSolicitudViaje,
        ValidacionSolicitudPagoDirecto,
        ValidacionRendicionCuentas,
    )
    from django.core.exceptions import ObjectDoesNotExist
    
    MODELO_MAP = {
        'fondos': ValidacionSolicitudFondos,
        'reposicion': ValidacionSolicitudReembolso,
        'viaje': ValidacionSolicitudViaje,
        'pago_directo': ValidacionSolicitudPagoDirecto,
        'rendicion': ValidacionRendicionCuentas,
    }
    
    modelo = MODELO_MAP[tipo]
    
    try:
        if tipo == 'rendicion':
            validacion = modelo.objects.get(rendicion=solicitud, usuarioValidador_id=revisor_id)
        else:
            validacion = modelo.objects.get(solicitud=solicitud, usuarioValidador_id=revisor_id)
    except ObjectDoesNotExist:
        return None
    
    return {
        'id': validacion.id,
        'codigoSeguimiento': validacion.codigoSeguimiento,
        'usuarioValidador_id': validacion.usuarioValidador_id,
        'usuarioRedactor_id': validacion.usuarioRedactor_id,
        'estado': validacion.estado,
        'comentarios': validacion.comentarios,
        'versionDocumento': validacion.versionDocumento,
        'fechaAsignacion': timezone.localtime(validacion.fechaAsignacion).strftime('%d/%m/%Y %H:%M'),
        'fechaResolucion': timezone.localtime(validacion.fechaResolucion).strftime('%d/%m/%Y %H:%M') if validacion.fechaResolucion else None,
    }