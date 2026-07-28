# spme/spme_presupuesto/services/presupuesto_tree/enums.py
from enum import Enum

class NodeType(str, Enum):
    PROYECTO = 'proyecto'
    ACTIVIDAD = 'actividad'
    TAREA = 'tarea'
    RESULTADO_ACTIVIDADES = 'resultado_actividades'
    RESULTADO_TAREAS = 'resultado_tareas'

class Direction(str, Enum):
    DOWN = 'down'
    UP = 'up'
    BOTH = 'both'

class DepthType(str, Enum):
    SELF = 'self'
    ALL = 'all'