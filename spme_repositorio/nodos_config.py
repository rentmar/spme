# spme/spme_repositorio/nodos_config.py
"""
Configuración centralizada de nodos habilitados para adjuntos.
Claves uniformadas con el campo `nodo_tipo` del árbol de repositorio.
"""

from spme_actividades.models import Actividad, TareaActividad
from spme_estructuracion_proyecto.models import (
    IndicadorProyecto,
    IndicadorObjetivoGeneral,
    IndicadorResultadoObjGral,
    IndicadorObjetivoEspecifico,
    IndicadorResultadoObjEspecifico,
    ProductoOE,
    ProductoResultadoOE,
    ResultadoOG, 
    ResultadoOE,
)
from spme_monitoreo.models import (
    SolicitudFondos,
)

NODOS_CONFIG = {
    # ================================================================
    # INDICADORES
    # ================================================================
    'indicador': {
        'modelo': IndicadorProyecto,
        'carpeta': 'indicadores',
        'acceso_repositorio': True,
    },
    'indicadorog': {
        'modelo': IndicadorObjetivoGeneral,
        'carpeta': 'indicador_og',
        'acceso_repositorio': True,
    },
    'indicadorrog': {
        'modelo': IndicadorResultadoObjGral,
        'carpeta': 'indicador_rog',
        'acceso_repositorio': True,
    },
    'indicadoroe': {
        'modelo': IndicadorObjetivoEspecifico,
        'carpeta': 'indicador_oe',
        'acceso_repositorio': True,
    },
    'indicadorroe': {
        'modelo': IndicadorResultadoObjEspecifico,
        'carpeta': 'indicador_roe',
        'acceso_repositorio': True,
    },
    # ================================================================
    # ACTIVIDAD Y TAREA
    # ================================================================
    'actividad': {
        'modelo': Actividad,
        'carpeta': 'actividades',
        'acceso_repositorio': True,
    },
    'tarea': {
        'modelo': TareaActividad,
        'carpeta': 'tareas',
        'acceso_repositorio': True,
    },
    # ================================================================
    # SOLICITUDES
    # ================================================================
    'solicitudfondosact': {
        'modelo': SolicitudFondos,
        'carpeta': 'solicitudes_fondos_actividad',
        'acceso_repositorio': True,
    },
    'solicitudfondostarea': {
        'modelo': SolicitudFondos,
        'carpeta': 'solicitudes_fondos_tarea',
        'acceso_repositorio': True,
    },
    # ================================================================
    # PRODUCTOS
    # ================================================================
    'productooe': {
        'modelo': ProductoOE,
        'carpeta': 'productos_oe',
        'acceso_repositorio': True,
    },
    'productoroe': {
        'modelo': ProductoResultadoOE,
        'carpeta': 'productos_roe',
        'acceso_repositorio': True,
    },
    # ================================================================
    # RESULTADOS
    # ================================================================
    'resultadoog':{
        'modelo':ResultadoOG,
        'carpeta': 'resultado_og',
        'acceso_repositorio': False,
    },
    'resultadooe':{
            'modelo':ResultadoOE,
            'carpeta': 'resultado_oe',
            'acceso_repositorio': False,
    },
        
}

# ================================================================
# FUNCIONES AUXILIARES
# ================================================================

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


def get_acceso_repositorio(tipo_objeto: str) -> bool:
    """Retorna si el tipo_objeto tiene acceso al repositorio."""
    config = NODOS_CONFIG.get(tipo_objeto)
    return config.get('acceso_repositorio', False) if config else False


def get_tipos_permitidos() -> list:
    """Retorna la lista de tipo_objeto permitidos."""
    return list(NODOS_CONFIG.keys())