# spme_mensajes/services/notificacion_service.py
from spme_mensajes.models import (
    MensajeUsuario,
    TipoMensaje,
    EstadoMensaje
)
from django.utils import timezone
import logging

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