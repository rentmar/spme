# spme/spme_presupuesto/services/presupuesto_tree_v3/depth_strategy.py
from typing import Union

class DepthStrategy:
    """
    Controla la expansión de niveles del árbol.
    """
    
    @staticmethod
    def can_expand(nivel_actual: int, depth: Union[str, int]) -> bool:
        """
        Determina si se puede expandir un nivel.
        
        Args:
            nivel_actual: Nivel actual del nodo.
            depth: Profundidad solicitada ('self', 'all', o número).
        
        Returns:
            True si se puede expandir, False en caso contrario.
        """
        if depth == 'self':
            return False
        
        if depth == 'all':
            return True
        
        if isinstance(depth, int):
            return nivel_actual < depth
        
        return False