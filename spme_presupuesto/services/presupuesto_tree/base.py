# spme/spme_presupuesto/services/presupuesto_tree/base.py
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from spme_presupuesto.services.presupuesto_tree.dto import TreeNode, BuildContext

class BasePresupuestoBuilder(ABC):
    """
    Clase base abstracta para todos los builders del árbol presupuestario.
    """

    @abstractmethod
    def get_node_type(self) -> str:
        """Retorna el tipo de nodo que construye este builder."""
        pass

    @abstractmethod
    def get_ids_by_parent(self, parent_id: int, parent_type: str) -> List[int]:
        """
        Retorna los IDs de los nodos hijos para un padre dado.
        """
        pass

    @abstractmethod
    def get_parent_id(self, child_id: int, parent_type: str) -> Optional[int]:
        """
        Retorna el ID del padre para un nodo hijo dado.
        """
        pass

    @abstractmethod
    def build(
        self,
        node_id: int,
        build_context: BuildContext,
        es_nodo_objetivo: bool = False,
        nivel: int = 0
    ) -> TreeNode:
        """
        Construye un TreeNode para el ID dado.
        """
        pass

    @abstractmethod
    def _extract_data(self, obj) -> Dict[str, Any]:
        """
        Extrae los datos específicos del modelo para el nodo.
        """
        pass

    def _get_formularios_actividad(
        self, actividad_id: int, build_context: BuildContext
    ) -> List[Dict[str, Any]]:
        """
        Obtiene los formularios asociados a una actividad desde el BuildContext.
        """
        if build_context and build_context.formularios_por_actividad:
            return build_context.formularios_por_actividad.get(actividad_id, [])
        return []

    def _get_formularios_tarea(
        self, tarea_id: int, build_context: BuildContext
    ) -> List[Dict[str, Any]]:
        """
        Obtiene los formularios asociados a una tarea desde el BuildContext.
        """
        if build_context and build_context.formularios_por_tarea:
            return build_context.formularios_por_tarea.get(tarea_id, [])
        return []

    def _calcular_ejecutado(self, formularios: List[Dict[str, Any]]) -> float:
        """
        Calcula el presupuesto ejecutado sumando formularios aprobados.
        """
        return sum(
            f.get('monto', 0)
            for f in formularios
            if f.get('estado') == 'aprobado'
        )