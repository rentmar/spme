from typing import Optional, List
from ..base import BaseNodeBuilder
from ..dto import TreeNode
from ..enums import NodeType
from django.apps import apps


class SolPagoDirectoActBuilder(BaseNodeBuilder):
    
    def get_node_type(self) -> str:
        return NodeType.SOL_PAGO_DIRECTO_ACT.value
    
    def get_ids_by_parent(self, parent_id, parent_type: str) -> List:
        print(f"[DEBUG BUILDER SPD-ACT] parent_id={parent_id}, parent_type='{parent_type}'")
        SolicitudPagoDirecto = apps.get_model('spme_monitoreo', 'SolicitudPagoDirecto')
        
        if parent_type == NodeType.ACTIVIDAD.value:
            ids = list(SolicitudPagoDirecto.objects.filter(
                actividad_id=parent_id, tarea_id__isnull=True
            ).values_list('id', flat=True))
            print(f"[DEBUG BUILDER SPD-ACT] Encontradas: {len(ids)}, IDs: {ids}")
            return ids
        return []
    
    def get_parent_id(self, child_id, parent_type: str) -> Optional[int]:
        try:
            SolicitudPagoDirecto = apps.get_model('spme_monitoreo', 'SolicitudPagoDirecto')
            obj = SolicitudPagoDirecto.objects.only('actividad_id').get(id=child_id)
            if parent_type == NodeType.ACTIVIDAD.value:
                return obj.actividad_id
        except Exception:
            pass
        return None
    
    def build(self, node_id, nivel=0, es_nodo_objetivo=False, depth_remaining=None, build_context=None) -> TreeNode:
        print(f"[DEBUG BUILDER SPD-ACT] Construyendo ID={node_id}")
        try:
            SolicitudPagoDirecto = apps.get_model('spme_monitoreo', 'SolicitudPagoDirecto')
            obj = SolicitudPagoDirecto.objects.select_related('usuario').prefetch_related('validaciones__usuarioValidador').get(id=node_id)
            validaciones = list(obj.validaciones.all())
            estado_consolidado = self._calcular_estado_consolidado(validaciones)
            
            datos = {
                'id': obj.id,
                'numero_formulario': obj.numeroFormulario or '',
                'usuario': obj.usuario.get_full_name() if obj.usuario else '',
                'fecha_solicitud': obj.fechaSolicitud.isoformat() if obj.fechaSolicitud else None,
                'monto_solicitado': str(obj.montoSolicitado) if obj.montoSolicitado else '0.00',
                'estado_consolidado': estado_consolidado,
                'subtipo': 'ACTIVIDAD',
                'validaciones': self._extraer_validaciones(validaciones),
                'total_validaciones': len(validaciones),
            }
            print(f"[DEBUG BUILDER SPD-ACT] Estado: {estado_consolidado}")
            return self._create_node(NodeType.SOL_PAGO_DIRECTO_ACT.value, obj.id, nivel, datos, es_nodo_objetivo, build_context=build_context)
        except Exception as e:
            print(f"[DEBUG BUILDER SPD-ACT] Error: {e}")
            raise ValueError(f"Pago Directo con ID {node_id} no encontrado")