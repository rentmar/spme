#TreeNode, TreeMetadata, TreeResponse, BuildContext
# Data Transfer Objects (TreeNode, TreeMetadata)
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class TreeNode:
    """
    Representa un nodo en el árbol jerárquico
    """
    tipo_nodo: str
    id: Any
    nivel: int
    datos: Dict[str, Any]
    hijos: List['TreeNode'] = field(default_factory=list)
    es_nodo_objetivo: bool = False
    actividades_relacionadas: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el nodo a diccionario para serialización JSON
        """
        return {
            'tipo_nodo': self.tipo_nodo,
            'id': self.id,
            'nivel': self.nivel,
            'datos': self.datos,
            'hijos': [hijo.to_dict() for hijo in self.hijos],
            'es_nodo_objetivo': self.es_nodo_objetivo,
            'actividades_relacionadas': self.actividades_relacionadas,
        }

@dataclass
class TreeMetadata:
    """
    Metadata de la operación del árbol
    """
    nodo_inicio: str
    profundidad_solicitada: str
    profundidad_alcanzada: int
    total_nodos: int
    direccion: str
    estructura: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'nodo_inicio': self.nodo_inicio,
            'profundidad_solicitada': self.profundidad_solicitada,
            'profundidad_alcanzada': self.profundidad_alcanzada,
            'total_nodos': self.total_nodos,
            'direccion': self.direccion,
            'estructura': self.estructura
        }

@dataclass
class TreeResponse:
    """
    Respuesta completa del endpoint de árbol
    """
    arbol: Optional[TreeNode]
    metadata: TreeMetadata
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'arbol': self.arbol.to_dict() if self.arbol else None,
            'metadata': self.metadata.to_dict()
        }


@dataclass
class BuildContext:
    """
    Contexto compartido durante la construcción del árbol
    """
    node_type: str
    node_id: Any
    depth: str
    direction: str
    current_level: int = 0
    max_depth: Optional[int] = None
    total_nodes: int = 0
    actividades_index: Dict[str, List[Dict]] = field(default_factory=dict)
    
    def increment_level(self) -> 'BuildContext':
        """
        Crea un nuevo contexto para el siguiente nivel
        """
        return BuildContext(
            node_type=self.node_type,
            node_id=self.node_id,
            depth=self.depth,
            direction=self.direction,
            current_level=self.current_level + 1,
            max_depth=self.max_depth,
            total_nodes=self.total_nodes,
            actividades_index=self.actividades_index 
        )

