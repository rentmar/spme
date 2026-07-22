#Constructor del nodo: Objetivo General
from typing import Optional, List
from ..base import BaseNodeBuilder
from ..dto import TreeNode
from ..enums import NodeType
from spme_estructuracion_proyecto.models import ObjetivoGeneralProyecto


class ObjetivoGeneralBuilder(BaseNodeBuilder):
    """Builder para nodos de tipo Objetivo General"""
    
    def get_node_type(self) -> str:
        return NodeType.OBJETIVO_GENERAL
    
    def get_ids_by_parent(self, parent_id, parent_type: str) -> List:
        """
        Retorna IDs de objetivos generales hijos del proyecto padre.
        """
        if parent_type == NodeType.PROYECTO:
            objetivos = ObjetivoGeneralProyecto.objects.filter(
                proyecto_id=parent_id
            ).values_list('id', flat=True)
            return list(objetivos)
        return []
    
    def get_parent_id(self, child_id, parent_type: str) -> Optional[int]:
        """
        Retorna el ID del proyecto padre del objetivo general.
        """
        if parent_type == NodeType.PROYECTO:
            try:
                objetivo = ObjetivoGeneralProyecto.objects.only('proyecto_id').get(id=child_id)
                return objetivo.proyecto_id
            except ObjetivoGeneralProyecto.DoesNotExist:
                return None
        return None
    
    def build(self, node_id, nivel=0, es_nodo_objetivo=False, depth_remaining=None, build_context=None) -> TreeNode:
        try:
            objetivo = ObjetivoGeneralProyecto.objects.select_related(
                'proyecto'
            ).get(id=node_id)
            
            datos = self._extract_data(objetivo)
            
            return self._create_node(
                tipo_nodo=NodeType.OBJETIVO_GENERAL,
                node_id=objetivo.id,
                nivel=nivel,
                datos=datos,
                es_nodo_objetivo=es_nodo_objetivo
            )
            
        except ObjetivoGeneralProyecto.DoesNotExist:
            raise ValueError(f"Objetivo General con ID {node_id} no encontrado")
    
    def _extract_data(self, objetivo: ObjetivoGeneralProyecto) -> dict:
        return {
            'codigo': objetivo.codigo or '',
            'descripcion': objetivo.descripcion or '',
            'supuestos': objetivo.supuestos or '',
            'riesgos': objetivo.riesgos or '',
            'proyecto_id': objetivo.proyecto.id if objetivo.proyecto else None,
            'proyecto_codigo': objetivo.proyecto.codigo if objetivo.proyecto else None,
            'proyecto_titulo': objetivo.proyecto.titulo if objetivo.proyecto else None
        }