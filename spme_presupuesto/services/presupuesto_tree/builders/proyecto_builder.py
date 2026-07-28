from typing import List, Optional, Dict, Any
from spme_presupuesto.services.presupuesto_tree.base import BasePresupuestoBuilder
from spme_presupuesto.services.presupuesto_tree.dto import TreeNode, BuildContext
from spme_presupuesto.services.presupuesto_tree.enums import NodeType
from spme_estructuracion_proyecto.models import Proyecto

class ProyectoPresupuestoBuilder(BasePresupuestoBuilder):

    def get_node_type(self) -> str:
        return NodeType.PROYECTO.value

    def get_ids_by_parent(self, parent_id: int, parent_type: str) -> List[int]:
        # Proyecto no tiene padre en este contexto
        return []

    def get_parent_id(self, child_id: int, parent_type: str) -> Optional[int]:
        # Proyecto es el nodo raíz
        return None

    def build(
        self,
        node_id: int,
        build_context: BuildContext,
        es_nodo_objetivo: bool = False,
        nivel: int = 0
    ) -> TreeNode:
        try:
            proyecto = Proyecto.objects.get(id=node_id)
        except Proyecto.DoesNotExist:
            raise ValueError(f"Proyecto con ID {node_id} no encontrado")

        # Datos del proyecto
        datos = self._extract_data(proyecto)

        return TreeNode(
            tipo_nodo=self.get_node_type(),
            id=node_id,
            nivel=nivel,
            es_nodo_virtual=False,
            es_nodo_objetivo=es_nodo_objetivo,
            datos=datos,
            formularios=[],
            hijos=[]
        )

    def _extract_data(self, proyecto: Proyecto) -> Dict[str, Any]:
        # Procedencia de fondos (referencia, no fuente de verdad)
        procedencias = []
        for pf in proyecto.procedencia_fondos.all():
            procedencias.append({
                'sigla': pf.sigla or '',
                'financiera': pf.financiera or ''
            })

        return {
            'codigo': proyecto.codigo or '',
            'titulo': proyecto.titulo or '',
            'descripcion': proyecto.descripcion or '',
            'presupuesto': float(proyecto.presupuesto or 0),
            'estado': proyecto.estado or '',
            'fecha_inicio': proyecto.fecha_inicio.isoformat() if proyecto.fecha_inicio else None,
            'fecha_finalizacion': proyecto.fecha_finalizacion.isoformat() if proyecto.fecha_finalizacion else None,
            'procedencia_fondos': procedencias,
            'moneda': 'BOB',
            'nota_procedencia': 'Referencia. Los desgloses por financiador en nodos inferiores son opcionales.'
        }