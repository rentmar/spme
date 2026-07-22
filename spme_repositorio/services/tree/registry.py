# NodeRegistry
# Registro de builders y relaciones
from typing import Dict, List, Optional, Type
from .base import BaseNodeBuilder
from .enums import NodeType


class NodeRegistry:
    """
    Registro central que mapea:
    - Tipos de nodo → Builders
    - Relaciones padre-hijo entre tipos de nodo
    
    Mapeo de Modelos a Nodos:
    ┌─────────────────────────────────┬──────────────────┐
    │ Modelo                          │ Nodo             │
    ├─────────────────────────────────┼──────────────────┤
    │ Proyecto                        │ proyecto         │
    │ ObjetivoGeneralProyecto         │ objetivogeneral  │
    └─────────────────────────────────┴──────────────────┘
    """
    
    def __init__(self):
        self._builders: Dict[str, BaseNodeBuilder] = {}
        self._tree_structure: Dict[str, dict] = {}
        self._initialize_structure()
    
    def _initialize_structure(self):
        """Define la estructura base del árbol (relaciones padre-hijo)"""
        self._tree_structure = {
            NodeType.PROYECTO.value: {
                'children': [NodeType.OBJETIVO_GENERAL.value],
                'parent': None,  # Es raíz
                'label': 'Proyecto',
                'model': 'Proyecto'
            },
            NodeType.OBJETIVO_GENERAL.value: {
                'children': [
                    NodeType.OBJETIVO_ESPECIFICO_OG.value,
                    NodeType.INDICADOR_OG.value,
                    NodeType.RESULTADO_OG.value,
                ], 
                'parent': NodeType.PROYECTO.value,
                'label': 'Objetivo General',
                'model': 'ObjetivoGeneralProyecto'
            },
            NodeType.OBJETIVO_ESPECIFICO_OG.value: {
                'children': [],
                'parent': NodeType.OBJETIVO_GENERAL.value,
                'label': 'Objetivo Especifico',
                'model': 'ObjetivoEspecificoProyecto'
            },
            NodeType.INDICADOR_OG.value: {           
                'children': [],
                'parent': NodeType.OBJETIVO_GENERAL.value,
                'label': 'Indicador OG',
                'model': 'IndicadorObjetivoGeneral'
            },
            NodeType.RESULTADO_OG.value: {           
                'children': [],
                'parent': NodeType.OBJETIVO_GENERAL.value,
                'label': 'Resultado OG',
                'model': 'ResultadoOG'
            },

        }
    
    def register_builder(self, node_type: str, builder: BaseNodeBuilder):
        """Registra un builder para un tipo de nodo"""
        self._builders[node_type] = builder
    
    def get_builder(self, node_type: str) -> BaseNodeBuilder:
        """Obtiene el builder para un tipo de nodo"""
        if node_type not in self._builders:
            raise ValueError(f"No hay builder registrado para el tipo: {node_type}")
        return self._builders[node_type]
    
    def get_children_types(self, node_type: str) -> List[str]:
        """Obtiene los tipos de nodos hijos para un tipo de nodo"""
        structure = self._tree_structure.get(node_type, {})
        return structure.get('children', [])
    
    def get_parent_type(self, node_type: str) -> Optional[str]:
        """Obtiene el tipo de nodo padre para un tipo de nodo"""
        structure = self._tree_structure.get(node_type, {})
        return structure.get('parent')
    
    def is_root(self, node_type: str) -> bool:
        """Verifica si un tipo de nodo es raíz"""
        return self.get_parent_type(node_type) is None
    
    def is_leaf(self, node_type: str) -> bool:
        """Verifica si un tipo de nodo es hoja"""
        return len(self.get_children_types(node_type)) == 0
    
    def has_builder(self, node_type: str) -> bool:
        """Verifica si existe un builder registrado para el tipo"""
        return node_type in self._builders
    
    def get_registered_types(self) -> List[str]:
        """Retorna todos los tipos de nodo registrados"""
        return list(self._builders.keys())
    
    def get_model_name(self, node_type: str) -> Optional[str]:
        """Retorna el nombre del modelo asociado al tipo de nodo"""
        structure = self._tree_structure.get(node_type, {})
        return structure.get('model')
    
    def get_structure_description(self, start_type: str) -> str:
        """Genera una descripción textual de la estructura desde un tipo"""
        parts = [self._tree_structure.get(start_type, {}).get('label', start_type)]
        current = start_type
        
        children = self.get_children_types(current)
        while children:
            child = children[0]
            parts.append(self._tree_structure.get(child, {}).get('label', child))
            current = child
            children = self.get_children_types(current)
        
        return ' > '.join(parts)



    