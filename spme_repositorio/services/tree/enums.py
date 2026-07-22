# NodeType, Direction, DepthType
#Tipo de nodo, direccion y profundidad
from enum import Enum


class NodeType(str, Enum):
    """
    Tipos de nodos disponibles en el Arbol
    """
    PROYECTO = 'proyecto'
    OBJETIVO_GENERAL = 'objetivogeneral'
    OBJETIVO_ESPECIFICO_OG = 'objetivoespecificoog'


class Direction(str, Enum):
    """
    Direccion de navegacion en el arbol
    """
    DOWN = 'down'    # Solo descendientes
    UP = 'up'        # Solo ancestros
    BOTH = 'both'    # Ambas direcciones

class DepthType(str, Enum):
    """
    Tipos de profundidad
    """
    SELF = 'self'    # Solo el nodo actual
    ALL = 'all'      # Expansión completa


