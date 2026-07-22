# BaseNodeBuilder
# Builder base abstracto
from abc import ABC, abstractmethod
from typing import Optional, List
from .dto import TreeNode, BuildContext


class BaseNodeBuilder(ABC):
    """
    Clase base abstracta para todos los builders de nodos
    """
    
    @abstractmethod
    def build(
        self, 
        node_id, 
        nivel: int = 0, 
        es_nodo_objetivo: bool = False,
        depth_remaining: Optional[int] = None,
        build_context: Optional['BuildContext'] = None
    ) -> TreeNode:
        """
        Construye un nodo del árbol
        """
        pass
    
    @abstractmethod
    def get_node_type(self) -> str:
        """
        Retorna el tipo de nodo que construye
        """
        pass
    
    def get_ids_by_parent(self, parent_id, parent_type: str) -> List:
        """
        Opcional: Retorna IDs de hijos dado un padre.
        Sobrescribir si el nodo tiene hijos.
        """
        return []
    
    def get_parent_id(self, child_id, parent_type: str) -> Optional[int]:
        """
        Opcional: Retorna ID del padre dado un hijo.
        Sobrescribir si el nodo tiene padre.
        """
        return None
    
    def _create_node(
        self,
        tipo_nodo: str,
        node_id,
        nivel: int,
        datos: dict,
        es_nodo_objetivo: bool = False
    ) -> TreeNode:
        """
        Método helper para crear instancias de TreeNode
        """
        #Convertir enum a string cuando es necesario
        if hasattr(tipo_nodo, 'value'):
            tipo_nodo = tipo_nodo.value
            
        return TreeNode(
            tipo_nodo=tipo_nodo,
            id=node_id,
            nivel=nivel,
            datos=datos,
            es_nodo_objetivo=es_nodo_objetivo
        )