from ..models import (
    PlanificacionVersion,
    HistorialCambioPlanificacion,
)
from ..utils.validators import (
    normalizar_accion,
    normalizar_tipo,
    validar_accion,
    validar_tipo,
)

def crear_version(proyecto_id, usuario_id, estado_anterior, motivo, historial_actividades):
    """
    Crea una nueva versión y registra el historial de cambios.
    Cualquier error → excepción → rollback.
    """
    ultima = PlanificacionVersion.objects.filter(
        proyecto_id=proyecto_id
    ).order_by('-version_numero').first()
    nuevo_numero = 1 if not ultima else ultima.version_numero + 1

    version = PlanificacionVersion.objects.create(
        proyecto_id=proyecto_id,
        version_numero=nuevo_numero,
        usuario_id=usuario_id,
        motivo=motivo,
        estado_anterior=estado_anterior,
        resumen={'total_cambios': len(historial_actividades)},
    )

    for item in historial_actividades:
        accion = normalizar_accion(item.get('accion'))
        tipo = normalizar_tipo(item.get('tipo', 'actividad'))
        validar_tipo(tipo)
        validar_accion(accion, tipo)

        HistorialCambioPlanificacion.objects.create(
            version=version,
            trackid=item.get('trackid'),
            tipo=tipo,
            accion=accion,
            columna=item.get('columna', ''),
            valor_anterior=item.get('valor_anterior'),
            valor_nuevo=item.get('valor_nuevo'),
            usuario=item.get('usuario', 'sistema'),
            timestamp=item.get('timestamp'),
            actividad_id=item.get('fila_id') or item.get('actividad_id', 0),
            actividad_codigo=item.get('actividad_codigo'),
        )

    return version