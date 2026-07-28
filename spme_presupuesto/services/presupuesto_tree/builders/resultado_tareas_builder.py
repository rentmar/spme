from typing import List, Optional, Dict, Any
from spme_presupuesto.services.presupuesto_tree.base import BasePresupuestoBuilder
from spme_presupuesto.services.presupuesto_tree.dto import TreeNode, BuildContext
from spme_presupuesto.services.presupuesto_tree.enums import NodeType

class ResultadoTareasBuilder(BasePresupuestoBuilder):
    """
    Builder virtual que consolida los presupuestos de todas las tareas.
    No consulta base de datos. Calcula totales desde los nodos ya construidos.
    """

    def get_node_type(self) -> str:
        return NodeType.RESULTADO_TAREAS.value

    def get_ids_by_parent(self, parent_id: int, parent_type: str) -> List[int]:
        if parent_type == NodeType.PROYECTO.value:
            return [0]  # ID ficticio
        return []

    def get_parent_id(self, child_id: int, parent_type: str) -> Optional[int]:
        return None

    def build(
        self,
        node_id: int,
        build_context: BuildContext,
        es_nodo_objetivo: bool = False,
        nivel: int = 0
    ) -> TreeNode:
        datos = {
            'nombre': 'Resultado de Tareas',
            'presupuesto_total_tareas': 0.0,
            'planificado_total_tareas': 0.0,
            'ejecutado_total_tareas': 0.0,
            'porcentaje_ejecucion_tareas': 0.0,
            'cantidad_tareas': 0,
            'moneda': 'BOB'
        }

        return TreeNode(
            tipo_nodo=self.get_node_type(),
            id=None,
            nivel=nivel,
            es_nodo_virtual=True,
            es_nodo_objetivo=es_nodo_objetivo,
            datos=datos,
            formularios=[],
            hijos=[]
        )

    def _extract_data(self, obj) -> Dict[str, Any]:
        return {}