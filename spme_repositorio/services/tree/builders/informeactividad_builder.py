from typing import Optional, List
from ..base import BaseNodeBuilder
from ..dto import TreeNode
from ..enums import NodeType
from django.apps import apps


class InformeActividadBuilder(BaseNodeBuilder):
    
    def get_node_type(self) -> str:
        return NodeType.INFORME_ACTIVIDAD.value
    
    def get_ids_by_parent(self, parent_id, parent_type: str) -> List:
        print(f"[DEBUG BUILDER INF-ACT] parent_id={parent_id}, parent_type='{parent_type}'")
        InformeActividadPrincipal = apps.get_model('spme_monitoreo', 'InformeActividadPrincipal')
        
        if parent_type == NodeType.ACTIVIDAD.value:
            ids = list(InformeActividadPrincipal.objects.filter(
                actividad_id=parent_id
            ).values_list('id', flat=True))
            print(f"[DEBUG BUILDER INF-ACT] Encontrados: {len(ids)}, IDs: {ids}")
            return ids
        return []
    
    def get_parent_id(self, child_id, parent_type: str) -> Optional[int]:
        try:
            InformeActividadPrincipal = apps.get_model('spme_monitoreo', 'InformeActividadPrincipal')
            obj = InformeActividadPrincipal.objects.only('actividad_id').get(id=child_id)
            if parent_type == NodeType.ACTIVIDAD.value:
                return obj.actividad_id
        except Exception:
            pass
        return None
    
    def build(self, node_id, nivel=0, es_nodo_objetivo=False, depth_remaining=None, build_context=None) -> TreeNode:
        print(f"[DEBUG BUILDER INF-ACT] Construyendo ID={node_id}")
        try:
            InformeActividadPrincipal = apps.get_model('spme_monitoreo', 'InformeActividadPrincipal')
            obj = InformeActividadPrincipal.objects.select_related('usuario').prefetch_related('validaciones__usuarioValidador').get(id=node_id)
            validaciones = list(obj.validaciones.all())
            estado_consolidado = self._calcular_estado_consolidado(validaciones)
            
            datos = {
                'id': obj.id,
                'numero_informe': obj.numeroInforme or '',
                'usuario': obj.usuario.get_full_name() if obj.usuario else '',
                'fecha_ejecucion': obj.fechaEjecucion.isoformat() if obj.fechaEjecucion else None,
                'presupuesto_planificado': str(obj.presupuestoPlanificado) if obj.presupuestoPlanificado else '0.00',
                'presupuesto_ejecutado': str(obj.presupuestoEjecutado) if obj.presupuestoEjecutado else '0.00',
                'estado_consolidado': estado_consolidado,
                'validaciones': self._extraer_validaciones(validaciones),
                'total_validaciones': len(validaciones),
            }
            print(f"[DEBUG BUILDER INF-ACT] Estado: {estado_consolidado}, Validaciones: {len(validaciones)}")
            return self._create_node(NodeType.INFORME_ACTIVIDAD.value, obj.id, nivel, datos, es_nodo_objetivo, build_context=build_context)
        except Exception as e:
            print(f"[DEBUG BUILDER INF-ACT] Error: {e}")
            raise ValueError(f"Informe Actividad con ID {node_id} no encontrado")