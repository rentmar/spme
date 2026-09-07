# spme/spme_presupuesto/services/presupuesto_tree_v3/dto.py
from typing import Optional, List, Dict, Any


class TreeNodeV3:
    """
    Nodo del árbol presupuestario V3.
    """
    
    def __init__(
        self,
        tipo_nodo: str,
        nivel: int = 0,
        id: Optional[int] = None,
        es_nodo_virtual: bool = False,
        es_contenedor: bool = False,
        es_nodo_objetivo: bool = False,
        datos: Optional[Dict[str, Any]] = None,
        formularios: Optional[List[Dict[str, Any]]] = None,
        hijos: Optional[List['TreeNodeV3']] = None,
    ):
        self.tipo_nodo = tipo_nodo
        self.nivel = nivel
        self.id = id
        self.es_nodo_virtual = es_nodo_virtual
        self.es_contenedor = es_contenedor
        self.es_nodo_objetivo = es_nodo_objetivo
        self.datos = datos or {}
        self.formularios = formularios or []
        self.hijos = hijos or []
    
    def add_hijo(self, hijo: 'TreeNodeV3') -> 'TreeNodeV3':
        """
        Agrega un hijo al nodo.
        """
        self.hijos.append(hijo)
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el nodo a diccionario.
        """
        result = {
            'tipo_nodo': self.tipo_nodo,
            'nivel': self.nivel,
            'es_nodo_virtual': self.es_nodo_virtual,
            'es_contenedor': self.es_contenedor,
            'es_nodo_objetivo': self.es_nodo_objetivo,
            'datos': self.datos,
            'formularios': self.formularios,
            'hijos': [hijo.to_dict() for hijo in self.hijos],
        }
        
        if self.id is not None:
            result['id'] = self.id
        
        return result


class TreeMetadataV3:
    """
    Metadata del árbol.
    """
    
    def __init__(
        self,
        nodo_inicio: str,
        profundidad_solicitada: str,
        profundidad_alcanzada: int,
        total_nodos: int,
        direccion: str = 'down',
    ):
        self.nodo_inicio = nodo_inicio
        self.profundidad_solicitada = profundidad_solicitada
        self.profundidad_alcanzada = profundidad_alcanzada
        self.total_nodos = total_nodos
        self.direccion = direccion
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'nodo_inicio': self.nodo_inicio,
            'profundidad_solicitada': self.profundidad_solicitada,
            'profundidad_alcanzada': self.profundidad_alcanzada,
            'total_nodos': self.total_nodos,
            'direccion': self.direccion,
            'version': 'v3',
        }


class TreeResponseV3:
    """
    Respuesta completa del árbol.
    """
    
    def __init__(self, arbol: TreeNodeV3, metadata: TreeMetadataV3):
        self.arbol = arbol
        self.metadata = metadata
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'arbol': self.arbol.to_dict(),
            'metadata': self.metadata.to_dict(),
        }