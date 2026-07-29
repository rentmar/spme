from ..serializers.planificacion import (
    ActividadActualizarSerializer,
    ActividadCrearSerializer,
    TareaActualizarSerializer,
    TareaCrearSerializer,
)
from ..services.actividades import actualizar_actividades, crear_actividades
from ..services.tareas import actualizar_tareas, crear_tareas
from ..services.seguimiento import crear_version


# ── Mapa de servicios: sección del payload → (serializer, servicio) ──
# Para activar/desactivar, comentar/descomentar líneas.
# Para añadir uno nuevo, agregar una entrada.

OPERACIONES = {
    'actividades_actualizar': {
        'serializer': ActividadActualizarSerializer,
        'servicio': actualizar_actividades,
        'extra_args': False,  # ¿El servicio necesita proyecto_id?
    },
    'actividades_nuevas': {
        'serializer': ActividadCrearSerializer,
        'servicio': crear_actividades,
        'extra_args': True,
    },
    # Descomentar cuando la grilla de tareas esté lista:
    # 'tareas_actualizar': {
    #     'serializer': TareaActualizarSerializer,
    #     'servicio': actualizar_tareas,
    #     'extra_args': False,
    # },
    # 'tareas_nuevas': {
    #     'serializer': TareaCrearSerializer,
    #     'servicio': crear_tareas,
    #     'extra_args': False,
    # },
}


def guardar_planificacion(payload, usuario_id):
    """
    Orquesta el guardado completo de la planificación.
    
    - Itera sobre OPERACIONES y ejecuta las que tengan datos en el payload.
    - Para añadir/quitar servicios, solo modificar el diccionario OPERACIONES.
    """
    metadatos = payload.get('metadatos_seguimiento', {})
    proyecto_id = metadatos.get('proyecto_id')

    if not proyecto_id:
        raise ValueError('metadatos_seguimiento.proyecto_id es requerido')

    # ── Ejecutar cada operación configurada ──
    for seccion, config in OPERACIONES.items():
        datos = payload.get(seccion)
        if not datos:
            continue

        serializer_class = config['serializer']
        servicio = config['servicio']

        serializer = serializer_class(data=datos, many=True)
        serializer.is_valid(raise_exception=True)

        if config['extra_args']:
            servicio(serializer.validated_data, proyecto_id)
        else:
            servicio(serializer.validated_data)

    # ── Seguimiento ──
    version = crear_version(
        proyecto_id=proyecto_id,
        usuario_id=usuario_id,
        estado_anterior=payload.get('estado_anterior', {}),
        motivo=metadatos.get('porque_modificacion', 'Sin motivo'),
        historial_actividades=payload.get('historial_actividades', []),
    )

    return {
        'mensaje': 'Planificación guardada exitosamente',
        'version_id': version.id,
        'version_numero': version.version_numero,
    }