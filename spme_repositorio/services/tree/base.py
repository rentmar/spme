# BaseNodeBuilder
# Builder base abstracto
from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from .dto import TreeNode, BuildContext

from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from .dto import TreeNode


class BaseNodeBuilder(ABC):
    """Clase base abstracta para todos los builders de nodos"""
    
    # Mapeo de node_type → campo en seleccionesSimples
    # True = es array, False = valor único
    SELECCIONES_MAPPING = {
        'objetivogeneral': {'campo': 'objetivoGeneralId', 'es_array': False},
        'objetivoespecificoog': {'campo': 'objetivoEspecificoId', 'es_array': False},
        'indicadoroe': {'campo': 'indicadorOEIds', 'es_array': True},
        'resultadooe': {'campo': 'resultadoOEId', 'es_array': False},
        'productooe': {'campo': 'productoOEId', 'es_array': False},
        'procesooe': {'campo': 'procesoEspecificoOEId', 'es_array': False},
        'indicadorroe': {'campo': 'indicadorResultadoOEIds', 'es_array': True},
        'productoroe': {'campo': 'productoResultadoOEIds', 'es_array': True},
        'procesoroe': {'campo': 'procesoResultadoOEId', 'es_array': False},
        'procesopoe': {'campo': 'procesoProductoOEId', 'es_array': False},
        'indicadorog': {'campo': 'indicadorOGIds', 'es_array': True},
        'resultadoog': {'campo': 'resultadoOGId', 'es_array': False},
        'indicadorrog': {'campo': 'indicadorResultadoOGIds', 'es_array': True},
        'procesorog': {'campo': 'procesoOGId', 'es_array': False},
    }
    
    @abstractmethod
    def build(
        self, 
        node_id, 
        nivel: int = 0, 
        es_nodo_objetivo: bool = False,
        depth_remaining: Optional[int] = None,
        build_context: Optional['BuildContext'] = None
    ) -> TreeNode:
        """Construye un nodo del árbol"""
        pass
    
    @abstractmethod
    def get_node_type(self) -> str:
        """Retorna el tipo de nodo que construye"""
        pass
    
    def get_ids_by_parent(self, parent_id, parent_type: str) -> List:
        """Opcional: Retorna IDs de hijos dado un padre"""
        return []
    
    def get_parent_id(self, child_id, parent_type: str) -> Optional[int]:
        """Opcional: Retorna ID del padre dado un hijo"""
        return None
    
    def get_actividades_relacionadas(
        self, 
        node_type: str, 
        node_id, 
        build_context: Optional['BuildContext'] = None
    ) -> List[Dict]:
        """
        Busca actividades relacionadas a este nodo usando el índice en build_context.
        """
        print(f"[DEBUG ACTIVIDADES] Buscando actividades para {node_type}:{node_id}")
        
        if not build_context or not build_context.actividades_index:
            print(f"[DEBUG ACTIVIDADES] Sin índice de actividades")
            return []
        
        key = f"{node_type}:{node_id}"
        actividades = build_context.actividades_index.get(key, [])
        
        print(f"[DEBUG ACTIVIDADES] Clave: '{key}' → Encontradas: {len(actividades)}")
        for act in actividades:
            print(f"[DEBUG ACTIVIDADES]   - ID: {act['id']}, Código: {act.get('codigo', 'N/A')}")
        
        return actividades
    
    def _create_node(
        self,
        tipo_nodo,
        node_id,
        nivel: int,
        datos: dict,
        es_nodo_objetivo: bool = False,
        build_context: Optional['BuildContext'] = None
    ) -> TreeNode:
        """Método helper para crear instancias de TreeNode"""
        if hasattr(tipo_nodo, 'value'):
            tipo_nodo = tipo_nodo.value
        
        # Obtener actividades relacionadas
        actividades = self.get_actividades_relacionadas(tipo_nodo, node_id, build_context)
        
        return TreeNode(
            tipo_nodo=tipo_nodo,
            id=node_id,
            nivel=nivel,
            datos=datos,
            es_nodo_objetivo=es_nodo_objetivo,
            actividades_relacionadas=actividades  # ← NUEVO
        )