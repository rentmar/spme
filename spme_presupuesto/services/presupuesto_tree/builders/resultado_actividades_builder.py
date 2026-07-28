from typing import List, Optional, Dict, Any
from spme_presupuesto.services.presupuesto_tree.base import BasePresupuestoBuilder
from spme_presupuesto.services.presupuesto_tree.dto import TreeNode, BuildContext
from spme_presupuesto.services.presupuesto_tree.enums import NodeType

class ResultadoActividadesBuilder(BasePresupuestoBuilder):
    """
    Builder virtual que consolida los presupuestos de todas las actividades.
    No consulta base de datos. Calcula totales desde los nodos ya construidos.
    """

    def get_node_type(self) -> str:
        return NodeType.RESULTADO_ACTIVIDADES.value

    def get_ids_by_parent(self, parent_id: int, parent_type: str) -> List[int]:
        # Nodo virtual: siempre existe uno solo por proyecto
        if parent_type == NodeType.PROYECTO.value:
            return [0]  # ID ficticio
        return []

    def get_parent_id(self, child_id: int, parent_type: str) -> Optional[int]:
        return None  # No se usa para nodos virtuales

    def build(
        self,
        node_id: int,
        build_context: BuildContext,
        es_nodo_objetivo: bool = False,
        nivel: int = 0
    ) -> TreeNode:
        # Los datos se calculan desde el build_context o se dejan en 0
        # El orchestrator los actualizará después de construir las actividades
        datos = {
            'nombre': 'Resultado de Actividades',
            'presupuesto_total': 0.0,
            'planificado_total': 0.0,
            'ejecutado_total': 0.0,
            'porcentaje_ejecucion_global': 0.0,
            'cantidad_actividades': 0,
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