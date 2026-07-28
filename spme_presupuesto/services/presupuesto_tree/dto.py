# spme/spme_presupuesto/services/presupuesto_tree/dto.py
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class TreeNode:
    tipo_nodo: str
    id: Optional[int]
    nivel: int
    es_nodo_virtual: bool = False
    es_nodo_objetivo: bool = False
    datos: Dict[str, Any] = field(default_factory=dict)
    formularios: List[Dict[str, Any]] = field(default_factory=list)
    hijos: List['TreeNode'] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'tipo_nodo': self.tipo_nodo,
            'id': self.id,
            'nivel': self.nivel,
            'es_nodo_virtual': self.es_nodo_virtual,
            'es_nodo_objetivo': self.es_nodo_objetivo,
            'datos': self.datos,
            'formularios': self.formularios,
            'hijos': [hijo.to_dict() for hijo in self.hijos]
        }


@dataclass
class TreeMetadata:
    nodo_inicio: str
    profundidad_solicitada: Any
    profundidad_alcanzada: int
    total_nodos: int
    direccion: str
    estructura: str
    actividades: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'nodo_inicio': self.nodo_inicio,
            'profundidad_solicitada': str(self.profundidad_solicitada),
            'profundidad_alcanzada': self.profundidad_alcanzada,
            'total_nodos': self.total_nodos,
            'direccion': self.direccion,
            'estructura': self.estructura,
            'actividades': self.actividades
        }


@dataclass
class BuildContext:
    formularios_por_actividad: Dict[int, List[Dict]] = field(default_factory=dict)
    formularios_por_tarea: Dict[int, List[Dict]] = field(default_factory=dict)
    actividades_incluidas: List[int] = field(default_factory=list)
    es_nodo_inicio: bool = False


@dataclass
class TreeResponse:
    arbol: TreeNode
    metadata: TreeMetadata

    def to_dict(self) -> Dict[str, Any]:
        return {
            'arbol': self.arbol.to_dict(),
            'metadata': self.metadata.to_dict()
        }