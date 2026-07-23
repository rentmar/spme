from typing import Optional, List
from ..base import BaseNodeBuilder
from ..dto import TreeNode
from ..enums import NodeType
from spme_estructuracion_proyecto.models import ResultadoOG


class ResultadoOGBuilder(BaseNodeBuilder):
    """Builder para nodos de tipo Resultado de Objetivo General"""
    
    def get_node_type(self) -> str:
        return NodeType.RESULTADO_OG.value
    
    def get_ids_by_parent(self, parent_id, parent_type: str) -> List:
        print(f"[DEBUG BUILDER ROG] get_ids_by_parent - parent_id={parent_id}, parent_type='{parent_type}'")
        print(f"[DEBUG BUILDER ROG] NodeType.OBJETIVO_GENERAL.value='{NodeType.OBJETIVO_GENERAL.value}'")
        print(f"[DEBUG BUILDER ROG] ¿Coincide?: {parent_type == NodeType.OBJETIVO_GENERAL.value}")
        
        if parent_type == NodeType.OBJETIVO_GENERAL.value:
            resultados = ResultadoOG.objects.filter(
                objetivo_general_id=parent_id
            )
            ids = list(resultados.values_list('id', flat=True))
            print(f"[DEBUG BUILDER ROG] Encontrados: {len(ids)} resultados, IDs: {ids}")
            return ids
        return []
    
    def get_parent_id(self, child_id, parent_type: str) -> Optional[int]:
        try:
            resultado = ResultadoOG.objects.only(
                'objetivo_general_id'
            ).get(id=child_id)
            
            if parent_type == NodeType.OBJETIVO_GENERAL.value:
                return resultado.objetivo_general_id
            
        except ResultadoOG.DoesNotExist:
            pass
        
        return None
    
    def build(self, node_id, nivel=0, es_nodo_objetivo=False, depth_remaining=None, build_context=None) -> TreeNode:
        try:
            resultado = ResultadoOG.objects.select_related(
                'objetivo_general'
            ).get(id=node_id)
            
            datos = self._extract_data(resultado)
            
            return self._create_node(
                tipo_nodo=NodeType.RESULTADO_OG.value,
                node_id=resultado.id,
                nivel=nivel,
                datos=datos,
                es_nodo_objetivo=es_nodo_objetivo,
                build_context=build_context
            )
            
        except ResultadoOG.DoesNotExist:
            raise ValueError(f"Resultado OG con ID {node_id} no encontrado")
    
    def _extract_data(self, resultado: ResultadoOG) -> dict:
        return {
            'codigo': resultado.codigo or '',
            'descripcion': resultado.descripcion or '',
            'supuestos': resultado.supuestos or '',
            'riesgos': resultado.riesgos or '',
            'objetivo_general_id': resultado.objetivo_general.id if resultado.objetivo_general else None,
        }