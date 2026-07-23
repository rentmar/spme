from typing import Optional, List
from ..base import BaseNodeBuilder
from ..dto import TreeNode
from ..enums import NodeType
from django.apps import apps


class TareaBuilder(BaseNodeBuilder):
    """Builder para nodos de tipo Tarea (subactividad)"""
    
    def get_node_type(self) -> str:
        return NodeType.TAREA.value
    
    def get_ids_by_parent(self, parent_id, parent_type: str) -> List:
        print(f"[DEBUG BUILDER TAREA] get_ids_by_parent - parent_id={parent_id}, parent_type='{parent_type}'")
        print(f"[DEBUG BUILDER TAREA] NodeType.ACTIVIDAD.value='{NodeType.ACTIVIDAD.value}'")
        print(f"[DEBUG BUILDER TAREA] ¿Coincide?: {parent_type == NodeType.ACTIVIDAD.value}")
        
        if parent_type == NodeType.ACTIVIDAD.value:
            TareaActividad = apps.get_model('spme_actividades', 'TareaActividad') 
            tareas = TareaActividad.objects.filter(
                actividad_id=parent_id
            )
            ids = list(tareas.values_list('id', flat=True))
            print(f"[DEBUG BUILDER TAREA] Encontradas: {len(ids)} tareas, IDs: {ids}")
            return ids
        return []
    
    def get_parent_id(self, child_id, parent_type: str) -> Optional[int]:
        try:
            TareaActividad = apps.get_model('spme_actividades', 'TareaActividad')
            tarea = TareaActividad.objects.only('actividad_id').get(id=child_id)
            
            if parent_type == NodeType.ACTIVIDAD.value:
                return tarea.actividad_id
            
        except Exception:
            pass
        return None
    
    def build(self, node_id, nivel=0, es_nodo_objetivo=False, depth_remaining=None, build_context=None) -> TreeNode:
        print(f"[DEBUG BUILDER TAREA] Construyendo tarea ID={node_id}")
        
        try:
            TareaActividad = apps.get_model('spme_actividades', 'TareaActividad')
            tarea = TareaActividad.objects.select_related('actividad').get(id=node_id)
            
            datos = self._extract_data(tarea)
            
            return self._create_node(
                tipo_nodo=NodeType.TAREA.value,
                node_id=tarea.id,
                nivel=nivel,
                datos=datos,
                es_nodo_objetivo=es_nodo_objetivo,
                build_context=build_context
            )
            
        except Exception as e:
            print(f"[DEBUG BUILDER TAREA] Error: {e}")
            raise ValueError(f"Tarea con ID {node_id} no encontrada")
    
    def _extract_data(self, tarea) -> dict:
        return {
            'codigo': tarea.codigo or '',
            'titulo': tarea.titulo or '',
            'descripcion': tarea.descripcion or '',
            'estado': tarea.get_estado_display() if tarea.estado else '',
            'fecha_ejecucion': tarea.fecha_ejecucion.isoformat() if tarea.fecha_ejecucion else None,
            'fecha_limite': tarea.fecha_limite.isoformat() if tarea.fecha_limite else None,
            'presupuesto': str(tarea.presupuesto) if tarea.presupuesto else '0.00',
            'actividad_id': tarea.actividad.id if tarea.actividad else None,
        }