from spme_actividades.models import TareaActividad


def actualizar_tareas(datos_validados):
    """
    Actualiza tareas existentes.
    Levanta excepción si alguna no existe → rollback.
    """
    for item in datos_validados:
        try:
            tarea = TareaActividad.objects.get(id=item['id'])
        except TareaActividad.DoesNotExist:
            raise Exception(f"Tarea con ID {item['id']} no encontrada")

        if 'codigo' in item:
            tarea.codigo = item['codigo']
        if 'titulo' in item:
            tarea.titulo = item['titulo']
        if 'descripcion' in item:
            tarea.descripcion = item['descripcion']
        if 'estado' in item:
            tarea.estado = item['estado']
        if 'fecha_ejecucion' in item:
            tarea.fecha_ejecucion = item['fecha_ejecucion']
        if 'fecha_limite' in item:
            tarea.fecha_limite = item['fecha_limite']
        if 'fecha_creacion' in item:
            tarea.fecha_creacion = item['fecha_creacion']
        if 'presupuesto' in item:
            tarea.presupuesto = item['presupuesto']
        if 'presupuestoDesglose' in item:
            tarea.presupuestoDesglose = item['presupuestoDesglose']
        if 'actividad_id' in item:
            tarea.actividad_id = item['actividad_id']

        tarea.save()


def crear_tareas(datos_validados):
    """
    Crea nuevas tareas.
    Cualquier error de BD → excepción → rollback.
    """
    for item in datos_validados:
        TareaActividad.objects.create(
            actividad_id=item['actividad_id'],
            codigo=item.get('codigo'),
            titulo=item.get('titulo', ''),
            descripcion=item.get('descripcion', ''),
            estado=item.get('estado', 'PEN'),
            fecha_ejecucion=item.get('fecha_ejecucion'),
            fecha_limite=item.get('fecha_limite'),
            presupuesto=item.get('presupuesto', 0),
            presupuestoDesglose=item.get('presupuestoDesglose'),
        )