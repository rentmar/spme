# services/utils/responsable_utils.py

def obtener_responsable(tipo_entidad, entidad):
    """Obtiene el responsable segun tipo de entidad"""
    mapeo = {
        'actividad': lambda e: getattr(e, 'responsable', None),
        'tarea': lambda e: getattr(e.actividad, 'responsable', None) if hasattr(e, 'actividad') else None,
        'actividad_pei': lambda e: getattr(e, 'responsable', None),
        'tarea_pei': lambda e: getattr(e.actividad, 'responsable', None) if hasattr(e, 'actividad') else None,
    }
    func = mapeo.get(tipo_entidad)
    return func(entidad) if func else None