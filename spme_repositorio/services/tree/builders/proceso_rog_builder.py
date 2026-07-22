from typing import Optional, List
from ..base import BaseNodeBuilder
from ..dto import TreeNode
from ..enums import NodeType
from spme_estructuracion_proyecto.models import Proceso


class ProcesoROGBuilder(BaseNodeBuilder):
    """Builder para nodos de tipo Proceso de Resultado de Objetivo General"""
    
    def get_node_type(self) -> str:
        return NodeType.PROCESO_ROG.value
    
    def get_ids_by_parent(self, parent_id, parent_type: str) -> List:
        print(f"[DEBUG BUILDER PROG] get_ids_by_parent - parent_id={parent_id}, parent_type='{parent_type}'")
        print(f"[DEBUG BUILDER PROG] NodeType.RESULTADO_OG.value='{NodeType.RESULTADO_OG.value}'")
        print(f"[DEBUG BUILDER PROG] ¿Coincide?: {parent_type == NodeType.RESULTADO_OG.value}")
        
        if parent_type == NodeType.RESULTADO_OG.value:
            procesos = Proceso.objects.filter(
                resultado_og_id=parent_id
            )
            ids = list(procesos.values_list('id', flat=True))
            print(f"[DEBUG BUILDER PROG] Encontrados: {len(ids)} procesos, IDs: {ids}")
            return ids
        return []
    
    def get_parent_id(self, child_id, parent_type: str) -> Optional[int]:
        try:
            proceso = Proceso.objects.only(
                'resultado_og_id'
            ).get(id=child_id)
            
            if parent_type == NodeType.RESULTADO_OG.value:
                return proceso.resultado_og_id
            
        except Proceso.DoesNotExist:
            pass
        
        return None
    
    def build(self, node_id, nivel=0, es_nodo_objetivo=False, depth_remaining=None, build_context=None) -> TreeNode:
        try:
            proceso = Proceso.objects.select_related(
                'resultado_og'
            ).get(id=node_id)
            
            datos = self._extract_data(proceso)
            
            return self._create_node(
                tipo_nodo=NodeType.PROCESO_ROG.value,
                node_id=proceso.id,
                nivel=nivel,
                datos=datos,
                es_nodo_objetivo=es_nodo_objetivo
            )
            
        except Proceso.DoesNotExist:
            raise ValueError(f"Proceso con ID {node_id} no encontrado")
    
    def _extract_data(self, proceso: Proceso) -> dict:
        return {
            'codigo': proceso.codigo or '',
            'titulo': proceso.titulo or '',
            'descripcion': proceso.descripcion or '',
            'resultado_og_id': proceso.resultado_og.id if proceso.resultado_og else None,
        }