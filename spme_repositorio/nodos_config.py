# spme/spme_repositorio/nodos_config.py
"""
Configuración centralizada de nodos habilitados para adjuntos.

Para agregar un nuevo nodo, solo agregar una entrada aquí.
"""

from spme_actividades.models import Actividad, TareaActividad
from spme_estructuracion_proyecto.models import IndicadorProyecto

NODOS_CONFIG = {
    # Indicadores
    'indicador': {
        'modelo': IndicadorProyecto,
        'carpeta': 'indicadores',
    },
    'indicador_og': {
        'modelo': IndicadorProyecto,
        'carpeta': 'indicador_og',
    },
    'indicador_rog': {
        'modelo': IndicadorProyecto,
        'carpeta': 'indicador_rog',
    },
    'indicador_oe': {
        'modelo': IndicadorProyecto,
        'carpeta': 'indicador_oe',
    },
    'indicador_roe': {
        'modelo': IndicadorProyecto,
        'carpeta': 'indicador_roe',
    },
    # Actividad y Tarea
    'actividad': {
        'modelo': Actividad,
        'carpeta': 'actividades',
    },
    'tarea': {
        'modelo': TareaActividad,
        'carpeta': 'tareas',
    },
}


def get_modelo(tipo_objeto: str):
    """Retorna la clase del modelo para un tipo_objeto."""
    config = NODOS_CONFIG.get(tipo_objeto)
    return config['modelo'] if config else None


def get_carpeta(tipo_objeto: str) -> str:
    """Retorna la carpeta en Garage para un tipo_objeto."""
    config = NODOS_CONFIG.get(tipo_objeto)
    if config is None:
        raise ValueError(f"Tipo de objeto no soportado: '{tipo_objeto}'")
    return config['carpeta']


def get_tipos_permitidos() -> list:
    """Retorna la lista de tipo_objeto permitidos."""
    return list(NODOS_CONFIG.keys())