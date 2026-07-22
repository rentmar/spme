from typing import Optional, List
from ..base import BaseNodeBuilder
from ..dto import TreeNode
from ..enums import NodeType
from spme_estructuracion_proyecto.models import IndicadorResultadoObjGral


class IndicadorROGBuilder(BaseNodeBuilder):
    """Builder para nodos de tipo Indicador de Resultado de Objetivo General"""
    
    def get_node_type(self) -> str:
        return NodeType.INDICADOR_ROG.value
    
    def get_ids_by_parent(self, parent_id, parent_type: str) -> List:
        print(f"[DEBUG BUILDER IROG] get_ids_by_parent - parent_id={parent_id}, parent_type='{parent_type}'")
        print(f"[DEBUG BUILDER IROG] NodeType.RESULTADO_OG.value='{NodeType.RESULTADO_OG.value}'")
        print(f"[DEBUG BUILDER IROG] ¿Coincide?: {parent_type == NodeType.RESULTADO_OG.value}")
        
        if parent_type == NodeType.RESULTADO_OG.value:
            indicadores = IndicadorResultadoObjGral.objects.filter(
                resultado_og_id=parent_id
            )
            ids = list(indicadores.values_list('id', flat=True))
            print(f"[DEBUG BUILDER IROG] Encontrados: {len(ids)} indicadores, IDs: {ids}")
            return ids
        return []
    
    def get_parent_id(self, child_id, parent_type: str) -> Optional[int]:
        try:
            indicador = IndicadorResultadoObjGral.objects.only(
                'resultado_og_id'
            ).get(id=child_id)
            
            if parent_type == NodeType.RESULTADO_OG.value:
                return indicador.resultado_og_id
            
        except IndicadorResultadoObjGral.DoesNotExist:
            pass
        
        return None
    
    def build(self, node_id, nivel=0, es_nodo_objetivo=False, depth_remaining=None, build_context=None) -> TreeNode:
        try:
            indicador = IndicadorResultadoObjGral.objects.select_related(
                'resultado_og'
            ).get(id=node_id)
            
            datos = self._extract_data(indicador)
            
            return self._create_node(
                tipo_nodo=NodeType.INDICADOR_ROG.value,
                node_id=indicador.id,
                nivel=nivel,
                datos=datos,
                es_nodo_objetivo=es_nodo_objetivo
            )
            
        except IndicadorResultadoObjGral.DoesNotExist:
            raise ValueError(f"Indicador Res. OG con ID {node_id} no encontrado")
    
    def _extract_data(self, indicador: IndicadorResultadoObjGral) -> dict:
        return {
            'codigo': indicador.codigo or '',
            'descripcion': indicador.descripcion or '',
            'redaccion': indicador.redaccion or '',
            'tipo': indicador.tipo or '',
            'frecuencia': indicador.frecuencia or '',
            'fuente_verificacion': indicador.fuente_verificacion or '',
            'baseline': indicador.baseline or '',
            'target_q1': indicador.target_q1 or '',
            'target_q2': indicador.target_q2 or '',
            'target_q3': indicador.target_q3 or '',
            'target_q4': indicador.target_q4 or '',
            'resultado_og_id': indicador.resultado_og.id if indicador.resultado_og else None,
        }
    