from typing import Optional
from .enums import DepthType


class DepthStrategy:
    """
    Controla la expansión de profundidad del árbol
    """
    
    def __init__(self, depth: str):
        """
        Args:
            depth: 'self', 'all', o número como string ('1', '2', etc.)
        """
        self.depth = depth
        self.max_depth = self._parse_depth(depth)
    
    def _parse_depth(self, depth: str) -> Optional[int]:
        """
        Convierte el parámetro depth a un valor numérico o None
        """
        if depth == DepthType.SELF:
            return 0
        if depth == DepthType.ALL:
            return None  # Ilimitado
        try:
            return int(depth)
        except (ValueError, TypeError):
            return None
    
    def should_continue(self, current_level: int) -> bool:
        """
        Determina si se debe continuar expandiendo en el nivel actual.
        
        Args:
            current_level: Nivel actual (0 = raíz)
            
        Returns:
            True si se debe expandir al siguiente nivel
        """
        if self.max_depth is None:
            return True  # 'all' - siempre continuar
        return current_level < self.max_depth
    
    def get_remaining_depth(self, current_level: int) -> Optional[int]:
        """
        Calcula profundidad restante para el siguiente nivel.
        
        Returns:
            Profundidad restante o None si es ilimitado
        """
        if self.max_depth is None:
            return None
        
        remaining = self.max_depth - current_level - 1
        return max(0, remaining)
    
    def is_self_only(self) -> bool:
        """
        Verifica si solo se debe mostrar el nodo actual
        """
        return self.depth == DepthType.SELF