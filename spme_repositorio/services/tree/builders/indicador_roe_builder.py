from typing import Optional, List
from ..base import BaseNodeBuilder
from ..dto import TreeNode
from ..enums import NodeType
from spme_estructuracion_proyecto.models import IndicadorResultadoObjEspecifico


class IndicadorROEBuilder(BaseNodeBuilder):
    
    def get_node_type(self) -> str:
        return NodeType.INDICADOR_ROE.value
    
    def get_ids_by_parent(self, parent_id, parent_type: str) -> List:
        print(f"[DEBUG BUILDER IROE] parent_id={parent_id}, parent_type='{parent_type}'")
        if parent_type == NodeType.RESULTADO_OE.value:
            ids = list(IndicadorResultadoObjEspecifico.objects.filter(
                resultado_obj_especifico_id=parent_id
            ).values_list('id', flat=True))
            print(f"[DEBUG BUILDER IROE] Encontrados: {len(ids)}, IDs: {ids}")
            return ids
        return []
    
    def get_parent_id(self, child_id, parent_type: str) -> Optional[int]:
        try:
            obj = IndicadorResultadoObjEspecifico.objects.only(
                'resultado_obj_especifico_id'
            ).get(id=child_id)
            if parent_type == NodeType.RESULTADO_OE.value:
                return obj.resultado_obj_especifico_id
        except IndicadorResultadoObjEspecifico.DoesNotExist:
            pass
        return None
    
    def build(self, node_id, nivel=0, es_nodo_objetivo=False, depth_remaining=None, build_context=None) -> TreeNode:
        obj = IndicadorResultadoObjEspecifico.objects.select_related(
            'resultado_obj_especifico'
        ).get(id=node_id)
        return self._create_node(
            NodeType.INDICADOR_ROE.value, 
            obj.id, 
            nivel, {
                'codigo': obj.codigo or '',
                'descripcion': obj.descripcion or '',
                'tipo': obj.tipo or '', 
                'frecuencia': obj.frecuencia or '',
                'resultado_oe_id': obj.resultado_obj_especifico.id if obj.resultado_obj_especifico else None,
            }, 
            es_nodo_objetivo,
            build_context=build_context,
        )