# spme/spme_presupuesto/services/presupuesto_tree/builders/tarea_builder.py
from typing import List, Optional, Dict, Any
from spme_presupuesto.services.presupuesto_tree.base import BasePresupuestoBuilder
from spme_presupuesto.services.presupuesto_tree.dto import TreeNode, BuildContext
from spme_presupuesto.services.presupuesto_tree.enums import NodeType
from spme_actividades.models import TareaActividad

class TareaPresupuestoBuilder(BasePresupuestoBuilder):

    def get_node_type(self) -> str:
        return NodeType.TAREA.value

    def get_ids_by_parent(self, parent_id: int, parent_type: str) -> List[int]:
        if parent_type == NodeType.ACTIVIDAD.value:
            return list(
                TareaActividad.objects
                .filter(actividad_id=parent_id)
                .values_list('id', flat=True)
            )
        return []

    def get_parent_id(self, child_id: int, parent_type: str) -> Optional[int]:
        if parent_type == NodeType.ACTIVIDAD.value:
            try:
                tarea = TareaActividad.objects.get(id=child_id)
                return tarea.actividad_id
            except TareaActividad.DoesNotExist:
                return None
        return None

    def build(
        self,
        node_id: int,
        build_context: BuildContext,
        es_nodo_objetivo: bool = False,
        nivel: int = 0
    ) -> TreeNode:
        try:
            tarea = TareaActividad.objects.get(id=node_id)
        except TareaActividad.DoesNotExist:
            raise ValueError(f"Tarea con ID {node_id} no encontrada")

        # Obtener formularios si existen en el contexto
        formularios = self._get_formularios_tarea(node_id, build_context)

        # Extraer datos
        datos = self._extract_data(tarea, formularios)

        return TreeNode(
            tipo_nodo=self.get_node_type(),
            id=node_id,
            nivel=nivel,
            es_nodo_virtual=False,
            es_nodo_objetivo=es_nodo_objetivo,
            datos=datos,
            formularios=formularios,
            hijos=[]
        )

    def _extract_data(self, tarea: TareaActividad, formularios: List[Dict] = None) -> Dict[str, Any]:
        if formularios is None:
            formularios = []

        ejecutado = self._calcular_ejecutado(formularios)
        presupuesto = float(tarea.presupuesto or 0)

        # Procesar desglose de presupuesto
        desglose = self._procesar_desglose(tarea.presupuestoDesglose)

        return {
            'codigo': tarea.codigo or '',
            'titulo': tarea.titulo or '',
            'descripcion': tarea.descripcion or '',
            'estado': tarea.estado or '',
            'estado_display': dict(TareaActividad.ESTADOS_TAREA).get(tarea.estado, ''),
            'presupuesto_tarea': presupuesto,
            'presupuesto_ejecutado': ejecutado,
            'porcentaje_ejecucion': round((ejecutado / presupuesto * 100), 1) if presupuesto > 0 else 0.0,
            'fecha_ejecucion': tarea.fecha_ejecucion.isoformat() if tarea.fecha_ejecucion else None,
            'fecha_limite': tarea.fecha_limite.isoformat() if tarea.fecha_limite else None,
            'presupuesto_desglose': desglose,
            'tiene_desglose': len(desglose) > 0,
            'cantidad_formularios': len(formularios),
            'moneda': 'BOB'
        }

    def _procesar_desglose(self, presupuestoDesglose) -> List[Dict[str, Any]]:
        """
        Procesa el JSON de presupuestoDesglose.
        Similar a procedencia_fondos de Actividad.
        """
        if not presupuestoDesglose:
            return []

        resultado = []
        for item in presupuestoDesglose:
            resultado.append({
                'id': item.get('id'),
                'nombre': item.get('nombre', ''),
                'monto': float(item.get('monto', 0)),
                'esExistente': item.get('esExistente', False),
                'tipo': 'registrado' if item.get('esExistente') else 'manual'
            })
        return resultado