from typing import Optional, List
from ..base import BaseNodeBuilder
from ..dto import TreeNode
from ..enums import NodeType
from spme_estructuracion_proyecto.models import IndicadorObjetivoGeneral


class IndicadorOGBuilder(BaseNodeBuilder):
    """Builder para nodos de tipo Indicador de Objetivo General"""
    
    def get_node_type(self) -> str:
        return NodeType.INDICADOR_OG.value
    
    def get_ids_by_parent(self, parent_id, parent_type: str) -> List:
        print(f"[DEBUG BUILDER IOG] get_ids_by_parent - parent_id={parent_id}, parent_type='{parent_type}'")
        print(f"[DEBUG BUILDER IOG] NodeType.OBJETIVO_GENERAL.value='{NodeType.OBJETIVO_GENERAL.value}'")
        print(f"[DEBUG BUILDER IOG] ¿Coincide?: {parent_type == NodeType.OBJETIVO_GENERAL.value}")
        
        if parent_type == NodeType.OBJETIVO_GENERAL.value:
            indicadores = IndicadorObjetivoGeneral.objects.filter(
                objetivo_general_id=parent_id
            )
            ids = list(indicadores.values_list('id', flat=True))
            print(f"[DEBUG BUILDER IOG] Encontrados: {len(ids)} indicadores, IDs: {ids}")
            return ids
        return []
    
    def get_parent_id(self, child_id, parent_type: str) -> Optional[int]:
        try:
            indicador = IndicadorObjetivoGeneral.objects.only(
                'objetivo_general_id'
            ).get(id=child_id)
            
            if parent_type == NodeType.OBJETIVO_GENERAL.value:
                return indicador.objetivo_general_id
            
        except IndicadorObjetivoGeneral.DoesNotExist:
            pass
        
        return None
    
    def build(self, node_id, nivel=0, es_nodo_objetivo=False, depth_remaining=None, build_context=None) -> TreeNode:
        try:
            indicador = IndicadorObjetivoGeneral.objects.select_related(
                'objetivo_general'
            ).get(id=node_id)
            
            datos = self._extract_data(indicador)
            
            return self._create_node(
                tipo_nodo=NodeType.INDICADOR_OG.value,
                node_id=indicador.id,
                nivel=nivel,
                datos=datos,
                es_nodo_objetivo=es_nodo_objetivo,
                build_context=build_context,
            )
            
        except IndicadorObjetivoGeneral.DoesNotExist:
            raise ValueError(f"Indicador OG con ID {node_id} no encontrado")
    
    def _extract_data(self, indicador: IndicadorObjetivoGeneral) -> dict:
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
            'objetivo_general_id': indicador.objetivo_general.id if indicador.objetivo_general else None,
        }