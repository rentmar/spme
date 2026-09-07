# spme/spme_presupuesto/services/presupuesto_tree_v3/enums.py
from enum import Enum

class TipoNodo(Enum):
    """
    Tipos de nodo del árbol presupuestario V3.
    """
    PROYECTO = 'proyecto'
    RESUMEN = 'resumen'
    CONTENEDOR_ACTIVIDADES = 'contenedor_actividades'
    ACTIVIDAD = 'actividad'
    CONTENEDOR_TAREAS = 'contenedor_tareas'
    TAREA = 'tarea'

class Direccion(Enum):
    """
    Dirección de expansión del árbol.
    """
    DOWN = 'down'
    UP = 'up'
    BOTH = 'both'

class Profundidad:
    """
    Constantes para profundidad.
    """
    SELF = 'self'
    ALL = 'all'