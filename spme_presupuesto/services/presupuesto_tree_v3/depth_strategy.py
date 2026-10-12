# spme/spme_presupuesto/services/presupuesto_tree_v3/depth_strategy.py
from typing import Union
from .enums import Profundidad

class DepthStrategy:
    """
    Controla la expansión de niveles del árbol.
    """
    
    @staticmethod
    def can_expand(
        nivel_nodo_objetivo: int,
        nivel_actual: int,
        depth: Union[str, int] = Profundidad.ALL,
    ) -> bool:
        # Si depth es 'all', siempre expande
        if depth == Profundidad.ALL or depth == 'all':
            return True

        # Si depth es 'self', no se expande ningún nivel descendiente
        if depth == Profundidad.SELF or depth == 'self':
            return False

        # Si depth es un entero (ej. 1, 2)
        try:
            depth_int = int(depth)
            diferencia_nivel = nivel_actual - nivel_nodo_objetivo
            return diferencia_nivel <= depth_int
        except (ValueError, TypeError):
            return True