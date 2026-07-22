from typing import Optional, List
from ..base import BaseNodeBuilder
from ..dto import TreeNode
from ..enums import NodeType
from spme_estructuracion_proyecto.models import Kpi


class KpiBuilder(BaseNodeBuilder):
    """Builder para nodos de tipo KPI"""
    
    def get_node_type(self) -> str:
        return NodeType.KPI.value
    
    def get_ids_by_parent(self, parent_id, parent_type: str) -> List:
        print(f"[DEBUG BUILDER KPI] get_ids_by_parent - parent_id={parent_id}, parent_type='{parent_type}'")
        print(f"[DEBUG BUILDER KPI] NodeType.OBJETIVO_GENERAL.value='{NodeType.OBJETIVO_GENERAL.value}'")
        print(f"[DEBUG BUILDER KPI] ¿Coincide?: {parent_type == NodeType.OBJETIVO_GENERAL.value}")
        
        if parent_type == NodeType.OBJETIVO_GENERAL.value:
            kpis = Kpi.objects.filter(
                objetivo_general_id=parent_id
            )
            ids = list(kpis.values_list('id', flat=True))
            print(f"[DEBUG BUILDER KPI] Encontrados: {len(ids)} KPIs, IDs: {ids}")
            return ids
        return []
    
    def get_parent_id(self, child_id, parent_type: str) -> Optional[int]:
        try:
            kpi = Kpi.objects.only('objetivo_general_id').get(id=child_id)
            
            if parent_type == NodeType.OBJETIVO_GENERAL.value:
                return kpi.objetivo_general_id
            
        except Kpi.DoesNotExist:
            pass
        
        return None
    
    def build(self, node_id, nivel=0, es_nodo_objetivo=False, depth_remaining=None, build_context=None) -> TreeNode:
        try:
            kpi = Kpi.objects.select_related('objetivo_general').get(id=node_id)
            datos = self._extract_data(kpi)
            
            return self._create_node(
                tipo_nodo=NodeType.KPI.value,
                node_id=kpi.id,
                nivel=nivel,
                datos=datos,
                es_nodo_objetivo=es_nodo_objetivo
            )
            
        except Kpi.DoesNotExist:
            raise ValueError(f"KPI con ID {node_id} no encontrado")
    
    def _extract_data(self, kpi: Kpi) -> dict:
        return {
            'codigo': kpi.codigo or '',
            'descripcion': kpi.descripcion or '',
            'objetivo_general_id': kpi.objetivo_general.id if kpi.objetivo_general else None,
        }