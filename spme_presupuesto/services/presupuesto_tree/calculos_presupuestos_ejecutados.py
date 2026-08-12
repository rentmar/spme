# spme/spme_presupuesto/services/presupuesto_tree/calculos_presupuestos_ejecutados.py
from spme_presupuesto.services.presupuesto_tree import presupuesto_orchestrator


def obtener_totales_actividad(actividad_id: int) -> dict:
    """
    Retorna los totales presupuestarios de una actividad.
    """
    response = presupuesto_orchestrator.build_tree('actividad', actividad_id, 'all', 'down')
    data = response.to_dict()
    datos = data['arbol']['datos']
    
    presupuesto_total = datos.get('presupuesto_actividad', 0)
    ejecutado_directo = datos.get('presupuesto_ejecutado', 0)
    presupuesto_tareas = datos.get('presupuesto_tareas', 0)
    ejecutado_tareas = datos.get('ejecutado_tareas', 0)
    ejecutado_total = ejecutado_directo + ejecutado_tareas
    porcentaje = round((ejecutado_total / presupuesto_total * 100), 1) if presupuesto_total > 0 else 0.0
    
    return {
        'id': actividad_id,
        'codigo': datos.get('codigo', ''),
        'nombre': datos.get('nombre', ''),
        'presupuesto_total': presupuesto_total,
        'presupuesto_ejecutado': ejecutado_total,
        'porcentaje_ejecucion': porcentaje,
        'cantidad_tareas': datos.get('cantidad_tareas', 0)
    }


def obtener_totales_tarea(tarea_id: int) -> dict:
    """
    Retorna los totales presupuestarios de una tarea.
    """
    response = presupuesto_orchestrator.build_tree('tarea', tarea_id, 'self', 'down')
    data = response.to_dict()
    datos = data['arbol']['datos']
    
    presupuesto_total = datos.get('presupuesto_tarea', 0)
    ejecutado_total = datos.get('presupuesto_ejecutado', 0)
    porcentaje = round((ejecutado_total / presupuesto_total * 100), 1) if presupuesto_total > 0 else 0.0
    
    return {
        'id': tarea_id,
        'codigo': datos.get('codigo', ''),
        'titulo': datos.get('titulo', ''),
        'presupuesto_total': presupuesto_total,
        'presupuesto_ejecutado': ejecutado_total,
        'porcentaje_ejecucion': porcentaje,
        'cantidad_formularios': datos.get('cantidad_formularios', 0)
    }