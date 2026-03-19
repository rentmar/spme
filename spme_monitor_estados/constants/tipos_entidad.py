# spme_monitor_estados/constants/tipos_entidad.py

"""
Constantes para tipos de entidad
"""

TIPOS_ENTIDAD = {
    'actividad': {
        'nombre': 'Actividad',
        'modelo': 'spme_actividades.Actividad',
        'campos': {
            'codigo': 'codigo',
            'nombre': 'nombreCorto',
            'responsable': 'responsable',
            'fecha_limite': 'fecha_cierre',
        }
    },
    'tarea': {
        'nombre': 'Tarea',
        'modelo': 'spme_actividades.TareaActividad',
        'campos': {
            'codigo': 'codigo',
            'nombre': 'titulo',
            'responsable': 'actividad__responsable',
            'fecha_limite': 'fecha_limite',
        }
    },
    'actividad_pei': {
        'nombre': 'Actividad PEI',
        'modelo': 'spme_actividades.ActividadPei',
        'campos': {
            'codigo': 'codigo',
            'nombre': 'nombreCorto',
            'responsable': 'responsable',
            'fecha_limite': 'fecha_cierre',
        }
    },
    'tarea_pei': {
        'nombre': 'Tarea PEI',
        'modelo': 'spme_actividades.TareaActividadPei',
        'campos': {
            'codigo': 'codigo',
            'nombre': 'titulo',
            'responsable': 'actividad__responsable',
            'fecha_limite': 'fecha_limite',
        }
    },
}