# spme/spme_presupuesto/services/presupuesto_tree_v3/registry.py
from typing import Dict, List, Optional, Type

from .enums import TipoNodo


class PresupuestoRegistryV3:
    """
    Registro de builders y relaciones jerárquicas.
    """
    
    def __init__(self):
        self._builders: Dict[str, Type] = {}
        self._children_map: Dict[str, List[str]] = {}
        self._parent_map: Dict[str, Optional[str]] = {}
        self._levels: Dict[str, int] = {}
        self._virtual: Dict[str, bool] = {}
        self._contenedor: Dict[str, bool] = {}
    
    def register(
        self,
        tipo_nodo: str,
        builder_class: Type,
        nivel: int,
        es_virtual: bool = False,
        es_contenedor: bool = False,
    ):
        """Registra un builder para un tipo de nodo."""
        self._builders[tipo_nodo] = builder_class
        self._levels[tipo_nodo] = nivel
        self._virtual[tipo_nodo] = es_virtual
        self._contenedor[tipo_nodo] = es_contenedor
    
    def register_children(self, tipo_nodo: str, children: List[str]):
        """Registra los tipos de hijos de un nodo."""
        self._children_map[tipo_nodo] = children
        for child in children:
            self._parent_map[child] = tipo_nodo
    
    def get_builder(self, tipo_nodo: str) -> Type:
        """Obtiene el builder para un tipo de nodo."""
        if tipo_nodo not in self._builders:
            raise ValueError(f"Tipo de nodo no registrado: {tipo_nodo}")
        return self._builders[tipo_nodo]
    
    def get_children_types(self, tipo_nodo: str) -> List[str]:
        """Obtiene los tipos de hijos de un nodo."""
        return self._children_map.get(tipo_nodo, [])
    
    def get_parent_type(self, tipo_nodo: str) -> Optional[str]:
        """Obtiene el tipo de padre de un nodo."""
        return self._parent_map.get(tipo_nodo)
    
    def get_nivel(self, tipo_nodo: str) -> int:
        """Obtiene el nivel de un tipo de nodo."""
        return self._levels.get(tipo_nodo, 0)
    
    def es_virtual(self, tipo_nodo: str) -> bool:
        """Verifica si un tipo de nodo es virtual."""
        return self._virtual.get(tipo_nodo, False)
    
    def es_contenedor(self, tipo_nodo: str) -> bool:
        """Verifica si un tipo de nodo es contenedor."""
        return self._contenedor.get(tipo_nodo, False)