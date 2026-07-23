from typing import Optional, List
from ..base import BaseNodeBuilder
from ..dto import TreeNode
from ..enums import NodeType
from django.apps import apps


class SolViajeSubBuilder(BaseNodeBuilder):
    
    def get_node_type(self) -> str:
        return NodeType.SOL_VIAJE_SUB.value
    
    def get_ids_by_parent(self, parent_id, parent_type: str) -> List:
        print(f"[DEBUG BUILDER SV-SUB] parent_id={parent_id}, parent_type='{parent_type}'")
        SolicitudViaje = apps.get_model('spme_monitoreo', 'SolicitudViaje')
        
        if parent_type == NodeType.TAREA.value:
            ids = list(SolicitudViaje.objects.filter(
                tarea_id=parent_id
            ).values_list('id', flat=True))
            print(f"[DEBUG BUILDER SV-SUB] Encontradas: {len(ids)}, IDs: {ids}")
            return ids
        return []
    
    def get_parent_id(self, child_id, parent_type: str) -> Optional[int]:
        try:
            SolicitudViaje = apps.get_model('spme_monitoreo', 'SolicitudViaje')
            obj = SolicitudViaje.objects.only('tarea_id').get(id=child_id)
            if parent_type == NodeType.TAREA.value:
                return obj.tarea_id
        except Exception:
            pass
        return None
    
    def build(self, node_id, nivel=0, es_nodo_objetivo=False, depth_remaining=None, build_context=None) -> TreeNode:
        print(f"[DEBUG BUILDER SV-SUB] Construyendo ID={node_id}")
        try:
            SolicitudViaje = apps.get_model('spme_monitoreo', 'SolicitudViaje')
            obj = SolicitudViaje.objects.select_related('usuario').prefetch_related('validaciones__usuarioValidador').get(id=node_id)
            validaciones = list(obj.validaciones.all())
            estado_consolidado = self._calcular_estado_consolidado(validaciones)
            
            datos = {
                'id': obj.id,
                'numero_formulario': obj.numeroFormulario or '',
                'usuario': obj.usuario.get_full_name() if obj.usuario else '',
                'fecha_solicitud': obj.fechaSolicitud.isoformat() if obj.fechaSolicitud else None,
                'monto_solicitado': str(obj.montoSolicitado) if obj.montoSolicitado else '0.00',
                'estado_consolidado': estado_consolidado,
                'subtipo': 'TAREA',
                'evento': obj.evento or '',
                'lugar_evento': obj.lugarEvento or '',
                'validaciones': self._extraer_validaciones(validaciones),
                'total_validaciones': len(validaciones),
            }
            print(f"[DEBUG BUILDER SV-SUB] Estado: {estado_consolidado}")
            return self._create_node(NodeType.SOL_VIAJE_SUB.value, obj.id, nivel, datos, es_nodo_objetivo, build_context=build_context)
        except Exception as e:
            print(f"[DEBUG BUILDER SV-SUB] Error: {e}")
            raise ValueError(f"Solicitud Viaje con ID {node_id} no encontrada")