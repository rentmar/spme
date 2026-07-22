from typing import Optional, List
from ..base import BaseNodeBuilder
from ..dto import TreeNode
from ..enums import NodeType
from spme_estructuracion_proyecto.models import IndicadorObjetivoEspecifico


class IndicadorOEBuilder(BaseNodeBuilder):
    
    def get_node_type(self) -> str:
        return NodeType.INDICADOR_OE.value
    
    def get_ids_by_parent(self, parent_id, parent_type: str) -> List:
        print(f"[DEBUG BUILDER IOE] parent_id={parent_id}, parent_type='{parent_type}'")
        if parent_type == NodeType.OBJETIVO_ESPECIFICO_OG.value:
            ids = list(IndicadorObjetivoEspecifico.objects.filter(
                objetivo_especifico_id=parent_id
            ).values_list('id', flat=True))
            print(f"[DEBUG BUILDER IOE] Encontrados: {len(ids)}, IDs: {ids}")
            return ids
        return []
    
    def get_parent_id(self, child_id, parent_type: str) -> Optional[int]:
        try:
            obj = IndicadorObjetivoEspecifico.objects.only('objetivo_especifico_id').get(id=child_id)
            if parent_type == NodeType.OBJETIVO_ESPECIFICO_OG.value:
                return obj.objetivo_especifico_id
        except IndicadorObjetivoEspecifico.DoesNotExist:
            pass
        return None
    
    def build(self, node_id, nivel=0, es_nodo_objetivo=False, depth_remaining=None, build_context=None) -> TreeNode:
        obj = IndicadorObjetivoEspecifico.objects.select_related('objetivo_especifico').get(id=node_id)
        return self._create_node(NodeType.INDICADOR_OE.value, obj.id, nivel, {
            'codigo': obj.codigo or '', 'descripcion': obj.descripcion or '',
            'tipo': obj.tipo or '', 'frecuencia': obj.frecuencia or '',
            'objetivo_especifico_id': obj.objetivo_especifico.id if obj.objetivo_especifico else None,
        }, es_nodo_objetivo)