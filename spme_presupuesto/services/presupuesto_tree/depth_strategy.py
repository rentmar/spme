# spme/spme_presupuesto/services/presupuesto_tree/depth_strategy.py
from typing import Union
from spme_presupuesto.services.presupuesto_tree.enums import DepthType

class DepthStrategy:
    """
    Controla la expansión de niveles en el árbol.
    
    - self: Solo el nodo raíz (nivel 0)
    - N numérico: N niveles de expansión
    - all: Sin límite de profundidad
    """

    def can_expand(self, nivel_actual: int, depth: Union[str, int]) -> bool:
        if depth == DepthType.SELF.value or depth == DepthType.SELF:
            return False #nunca expandir con self
        if depth == DepthType.ALL.value or depth == DepthType.ALL:
            return True #siempre expandir con all
        if isinstance(depth, int) or (isinstance(depth, str) and depth.isdigit()):
            depth_int = int(depth)
            return nivel_actual < depth_int
        return False

    def get_remaining_depth(self, nivel_actual: int, depth: Union[str, int]) -> int:
        if depth == DepthType.ALL.value or depth == DepthType.ALL:
            return -1  # Sin límite
        if isinstance(depth, int) or (isinstance(depth, str) and depth.isdigit()):
            depth_int = int(depth)
            return max(0, depth_int - nivel_actual)
        return 0