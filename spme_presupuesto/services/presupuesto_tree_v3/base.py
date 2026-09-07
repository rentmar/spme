# spme/spme_presupuesto/services/presupuesto_tree_v3/base.py
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

from .dto import TreeNodeV3
from .calculos import CalculosPresupuestariosV3


class BaseBuilderV3(ABC):
    """
    Builder base abstracto para V3.
    """
    
    def __init__(self, calculos: CalculosPresupuestariosV3):
        self.calculos = calculos
    
    @abstractmethod
    def get_tipo_nodo(self) -> str:
        """
        Retorna el tipo de nodo que construye este builder.
        """
        pass
    
    @abstractmethod
    def build(
        self,
        id: Optional[int] = None,
        nivel: int = 0,
        es_nodo_objetivo: bool = False,
    ) -> TreeNodeV3:
        """
        Construye el nodo.
        """
        pass
    
    @abstractmethod
    def get_ids_by_parent(self, parent_id: int) -> List[int]:
        """
        Obtiene IDs de nodos hijos dado un padre.
        """
        pass
    
    @abstractmethod
    def get_parent_id(self, id: int) -> Optional[int]:
        """
        Obtiene el ID del padre dado un ID de nodo.
        """
        pass
    
    def _calcular_ejecutado(
        self,
        formularios: List[Dict[str, Any]],
    ) -> float:
        """
        Calcula el ejecutado según regla de negocio.
        """
        return self.calculos.calcular_ejecutado_formularios(formularios)
    
    def _calcular_porcentaje(
        self,
        ejecutado: float,
        planificado: float,
    ) -> float:
        """
        Calcula el porcentaje de ejecución.
        """
        return self.calculos.calcular_porcentaje(ejecutado, planificado)