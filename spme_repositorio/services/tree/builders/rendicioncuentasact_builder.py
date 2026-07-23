from typing import Optional, List
from ..base import BaseNodeBuilder
from ..dto import TreeNode
from ..enums import NodeType
from django.apps import apps


class RendicionCuentasActBuilder(BaseNodeBuilder):
    
    def get_node_type(self) -> str:
        return NodeType.RENDICION_CUENTAS_ACT.value
    
    def get_ids_by_parent(self, parent_id, parent_type: str) -> List:
        print(f"[DEBUG BUILDER RC-ACT] parent_id={parent_id}, parent_type='{parent_type}'")
        RendicionCuentas = apps.get_model('spme_monitoreo', 'RendicionCuentas')
        
        if parent_type == NodeType.ACTIVIDAD.value:
            ids = list(RendicionCuentas.objects.filter(
                actividad_id=parent_id, tarea_id__isnull=True
            ).values_list('id', flat=True))
            print(f"[DEBUG BUILDER RC-ACT] Encontradas: {len(ids)}, IDs: {ids}")
            return ids
        return []
    
    def get_parent_id(self, child_id, parent_type: str) -> Optional[int]:
        try:
            RendicionCuentas = apps.get_model('spme_monitoreo', 'RendicionCuentas')
            obj = RendicionCuentas.objects.only('actividad_id').get(id=child_id)
            if parent_type == NodeType.ACTIVIDAD.value:
                return obj.actividad_id
        except Exception:
            pass
        return None
    
    def build(self, node_id, nivel=0, es_nodo_objetivo=False, depth_remaining=None, build_context=None) -> TreeNode:
        print(f"[DEBUG BUILDER RC-ACT] Construyendo ID={node_id}")
        try:
            RendicionCuentas = apps.get_model('spme_monitoreo', 'RendicionCuentas')
            obj = RendicionCuentas.objects.select_related('usuario').prefetch_related('validaciones__usuarioValidador').get(id=node_id)
            validaciones = list(obj.validaciones.all())
            estado_consolidado = self._calcular_estado_consolidado(validaciones)
            
            datos = {
                'id': obj.id,
                'numero_formulario': obj.numeroFormulario or '',
                'usuario': obj.usuario.get_full_name() if obj.usuario else '',
                'fecha_rendicion': obj.fechaRendicion.isoformat() if obj.fechaRendicion else None,
                'monto_asignado': str(obj.montoAsignado) if obj.montoAsignado else '0.00',
                'monto_descargado': str(obj.montoDescargado) if obj.montoDescargado else '0.00',
                'saldo': str(obj.saldo) if obj.saldo else '0.00',
                'estado_consolidado': estado_consolidado,
                'subtipo': 'ACTIVIDAD',
                'validaciones': self._extraer_validaciones(validaciones),
                'total_validaciones': len(validaciones),
            }
            print(f"[DEBUG BUILDER RC-ACT] Estado: {estado_consolidado}")
            return self._create_node(NodeType.RENDICION_CUENTAS_ACT.value, obj.id, nivel, datos, es_nodo_objetivo, build_context=build_context)
        except Exception as e:
            print(f"[DEBUG BUILDER RC-ACT] Error: {e}")
            raise ValueError(f"Rendicion con ID {node_id} no encontrada")