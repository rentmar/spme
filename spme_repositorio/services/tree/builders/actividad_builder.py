from typing import Optional, List
from ..base import BaseNodeBuilder
from ..dto import TreeNode
from ..enums import NodeType
from django.apps import apps


class ActividadBuilder(BaseNodeBuilder):
    """Builder para nodos de tipo Actividad"""
    
    def get_node_type(self) -> str:
        return NodeType.ACTIVIDAD.value
    
    def get_ids_by_parent(self, parent_id, parent_type: str) -> List:
        print(f"[DEBUG BUILDER ACT] get_ids_by_parent - parent_id={parent_id}, parent_type='{parent_type}'")
        
        # La actividad no tiene padre fijo, pero si se consulta desde un nodo de estructura,
        # se usa el índice de actividades del build_context
        return []
    
    def get_parent_id(self, child_id, parent_type: str) -> Optional[int]:
        # Una actividad puede tener múltiples padres (transversal)
        # Se resuelve vía estructuraProcedencia
        return None
    
    def build(self, node_id, nivel=0, es_nodo_objetivo=False, depth_remaining=None, build_context=None) -> TreeNode:
        print(f"[DEBUG BUILDER ACT] Construyendo actividad ID={node_id}")
        
        try:
            Actividad = apps.get_model('spme_actividades', 'Actividad')  # Ajusta el nombre de la app
            
            actividad = Actividad.objects.select_related(
                'tipo', 'proyecto', 'responsable'
            ).get(id=node_id, estaInactiva=False)
            
            datos = self._extract_data(actividad)
            
            return self._create_node(
                tipo_nodo=NodeType.ACTIVIDAD.value,
                node_id=actividad.id,
                nivel=nivel,
                datos=datos,
                es_nodo_objetivo=es_nodo_objetivo,
                build_context=build_context
            )
            
        except Exception as e:
            print(f"[DEBUG BUILDER ACT] Error: {e}")
            raise ValueError(f"Actividad con ID {node_id} no encontrada o inactiva")
    
    def _extract_data(self, actividad) -> dict:
        return {
            'codigo': actividad.codigo or '',
            'nombre_corto': actividad.nombreCorto or '',
            'descripcion': actividad.descripcion or '',
            'estado': actividad.get_estado_display() if actividad.estado else '',
            'fecha_programada': actividad.fecha_programada.isoformat() if actividad.fecha_programada else None,
            'fecha_inicio': actividad.fecha_inicio.isoformat() if actividad.fecha_inicio else None,
            'fecha_cierre': actividad.fecha_cierre.isoformat() if actividad.fecha_cierre else None,
            'presupuesto': str(actividad.presupuesto) if actividad.presupuesto else '0.00',
            'tipo_actividad': actividad.tipo.tipo_actividad if actividad.tipo else None,
            'responsable': actividad.responsable.get_full_name() if actividad.responsable else None,
            'proyecto_id': actividad.proyecto.id if actividad.proyecto else None,
        }