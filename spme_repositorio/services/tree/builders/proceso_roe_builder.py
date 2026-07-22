from typing import Optional, List
from ..base import BaseNodeBuilder
from ..dto import TreeNode
from ..enums import NodeType
from spme_estructuracion_proyecto.models import Proceso


class ProcesoROEBuilder(BaseNodeBuilder):
    
    def get_node_type(self) -> str:
        return NodeType.PROCESO_ROE.value
    
    def get_ids_by_parent(self, parent_id, parent_type: str) -> List:
        print(f"[DEBUG BUILDER PROCROE] parent_id={parent_id}, parent_type='{parent_type}'")
        if parent_type == NodeType.RESULTADO_OE.value:
            ids = list(Proceso.objects.filter(
                resultado_oe_id=parent_id
            ).values_list('id', flat=True))
            print(f"[DEBUG BUILDER PROCROE] Encontrados: {len(ids)}, IDs: {ids}")
            return ids
        return []
    
    def get_parent_id(self, child_id, parent_type: str) -> Optional[int]:
        try:
            obj = Proceso.objects.only('resultado_oe_id').get(id=child_id)
            if parent_type == NodeType.RESULTADO_OE.value:
                return obj.resultado_oe_id
        except Proceso.DoesNotExist:
            pass
        return None
    
    def build(self, node_id, nivel=0, es_nodo_objetivo=False, depth_remaining=None, build_context=None) -> TreeNode:
        obj = Proceso.objects.get(id=node_id)
        return self._create_node(NodeType.PROCESO_ROE.value, obj.id, nivel, {
            'codigo': obj.codigo or '', 'titulo': obj.titulo or '',
            'descripcion': obj.descripcion or '',
        }, es_nodo_objetivo)