#Builder del nodo objetivoespecificoog
from typing import Optional, List
from ..base import BaseNodeBuilder
from ..dto import TreeNode
from ..enums import NodeType
from spme_estructuracion_proyecto.models import ObjetivoEspecificoProyecto


class ObjetivoEspecificoOGBuilder(BaseNodeBuilder):
    """Builder para nodos de tipo Objetivo Específico de Objetivo General"""
    
    def get_node_type(self) -> str:
        return NodeType.OBJETIVO_ESPECIFICO_OG.value
    
    def get_ids_by_parent(self, parent_id, parent_type: str) -> List:
        """
        Retorna IDs de objetivos específicos hijos de un objetivo general.
        """
        print(f"[DEBUG BUILDER OE] get_ids_by_parent - parent_id={parent_id}, parent_type='{parent_type}'")
        print(f"[DEBUG BUILDER OE] NodeType.OBJETIVO_GENERAL.value='{NodeType.OBJETIVO_GENERAL.value}'")
        print(f"[DEBUG BUILDER OE] ¿Coincide?: {parent_type == NodeType.OBJETIVO_GENERAL.value}")
        
        if parent_type == NodeType.OBJETIVO_GENERAL.value:
            objetivos = ObjetivoEspecificoProyecto.objects.filter(
                objetivo_general_id=parent_id
            )
            ids = list(objetivos.values_list('id', flat=True))
            print(f"[DEBUG BUILDER OE] Encontrados: {len(ids)} objetivos, IDs: {ids}")
            return ids
        return []
    
    def get_parent_id(self, child_id, parent_type: str) -> Optional[int]:
        """Retorna el ID del padre según el tipo solicitado."""
        try:
            objetivo = ObjetivoEspecificoProyecto.objects.only(
                'objetivo_general_id', 'proyecto_id'
            ).get(id=child_id)
            
            if parent_type == NodeType.OBJETIVO_GENERAL.value:
                return objetivo.objetivo_general_id
            elif parent_type == NodeType.PROYECTO.value:
                return objetivo.proyecto_id
            
        except ObjetivoEspecificoProyecto.DoesNotExist:
            pass
        
        return None
    
    def build(self, node_id, nivel=0, es_nodo_objetivo=False, depth_remaining=None, build_context=None) -> TreeNode:
        try:
            objetivo = ObjetivoEspecificoProyecto.objects.select_related(
                'proyecto', 'objetivo_general'
            ).get(id=node_id)
            
            datos = self._extract_data(objetivo)
            
            return self._create_node(
                tipo_nodo=NodeType.OBJETIVO_ESPECIFICO_OG.value,
                node_id=objetivo.id,
                nivel=nivel,
                datos=datos,
                es_nodo_objetivo=es_nodo_objetivo
            )
            
        except ObjetivoEspecificoProyecto.DoesNotExist:
            raise ValueError(f"Objetivo Especifico con ID {node_id} no encontrado")
    
    def _extract_data(self, objetivo: ObjetivoEspecificoProyecto) -> dict:
        return {
            'codigo': objetivo.codigo or '',
            'descripcion': objetivo.descripcion or '',
            'supuestos': objetivo.supuestos or '',
            'riesgos': objetivo.riesgos or '',
            'proyecto_id': objetivo.proyecto.id if objetivo.proyecto else None,
            'proyecto_codigo': objetivo.proyecto.codigo if objetivo.proyecto else None,
            'objetivo_general_id': objetivo.objetivo_general.id if objetivo.objetivo_general else None,
        }