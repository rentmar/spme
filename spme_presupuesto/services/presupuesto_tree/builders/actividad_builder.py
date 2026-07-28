# spme/spme_presupuesto/services/presupuesto_tree/builders/actividad_builder.py
from typing import List, Optional, Dict, Any
from spme_presupuesto.services.presupuesto_tree.base import BasePresupuestoBuilder
from spme_presupuesto.services.presupuesto_tree.dto import TreeNode, BuildContext
from spme_presupuesto.services.presupuesto_tree.enums import NodeType
from spme_actividades.models import Actividad

ESTADOS_EXCLUIDOS = ['CRD']

class ActividadPresupuestoBuilder(BasePresupuestoBuilder):

    def get_node_type(self) -> str:
        return NodeType.ACTIVIDAD.value

    def get_ids_by_parent(self, parent_id: int, parent_type: str) -> List[int]:
        if parent_type == NodeType.PROYECTO.value:
            return list(
                Actividad.objects
                .filter(
                    proyecto_id=parent_id,
                    estaInactiva=False
                )
                .exclude(estado__in=ESTADOS_EXCLUIDOS)
                .values_list('id', flat=True)
            )
        return []

    def get_parent_id(self, child_id: int, parent_type: str) -> Optional[int]:
        if parent_type == NodeType.PROYECTO.value:
            try:
                actividad = Actividad.objects.get(id=child_id)
                return actividad.proyecto_id
            except Actividad.DoesNotExist:
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
            actividad = Actividad.objects.get(id=node_id)
        except Actividad.DoesNotExist:
            raise ValueError(f"Actividad con ID {node_id} no encontrada")

        # Verificar criterio de inclusión si se consulta directamente
        if es_nodo_objetivo:
            if actividad.estado in ESTADOS_EXCLUIDOS or actividad.estaInactiva:
                raise ValueError(
                    f"Actividad {node_id} no incluida en el árbol presupuestario. "
                    f"Estado: {actividad.estado}, Inactiva: {actividad.estaInactiva}"
                )

        # Obtener formularios si existen en el contexto
        formularios = self._get_formularios_actividad(node_id, build_context)

        # Extraer datos
        datos = self._extract_data(actividad, formularios)

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

    def _extract_data(self, actividad: Actividad, formularios: List[Dict] = None) -> Dict[str, Any]:
        if formularios is None:
            formularios = []

        ejecutado = self._calcular_ejecutado(formularios)
        presupuesto = float(actividad.presupuesto or 0)

        # Procesar procedencia_fondos
        procedencias = self._procesar_procedencia(actividad.procedencia_fondos)

        # Determinar el nombre a mostrar
        nombre = actividad.nombreCorto or actividad.descripcion or ''

        return {
            'codigo': actividad.codigo or '',
            'nombre': nombre[:100] if nombre else '',  # Truncar para display
            'descripcion': actividad.descripcion or '',
            'estado': actividad.estado or '',
            'estado_display': dict(Actividad.ESTADOS_ACTIVIDAD).get(actividad.estado, ''),
            'presupuesto_actividad': presupuesto,
            'presupuesto_ejecutado': ejecutado,
            'porcentaje_ejecucion': round((ejecutado / presupuesto * 100), 1) if presupuesto > 0 else 0.0,
            'fecha_inicio': actividad.fecha_inicio.isoformat() if actividad.fecha_inicio else None,
            'fecha_cierre': actividad.fecha_cierre.isoformat() if actividad.fecha_cierre else None,
            'responsable': actividad.responsable.correo if actividad.responsable else '',
            'procedencia_fondos': procedencias,
            'tiene_desglose': len(procedencias) > 0,
            'cantidad_formularios': len(formularios),
            'moneda': 'BOB'
        }

    def _procesar_procedencia(self, procedencia_fondos) -> List[Dict[str, Any]]:
        """
        Procesa el JSON de procedencia_fondos.
        Formato esperado:
        [
            {"id": 2, "nombre": "GOBAL", "monto": 5000, "esExistente": true},
            {"id": 1785..., "nombre": "GAMLP", "monto": 500, "esExistente": false}
        ]
        """
        if not procedencia_fondos:
            return []

        resultado = []
        for pf in procedencia_fondos:
            resultado.append({
                'id': pf.get('id'),
                'nombre': pf.get('nombre', ''),
                'monto': float(pf.get('monto', 0)),
                'esExistente': pf.get('esExistente', False),
                'tipo': 'registrado' if pf.get('esExistente') else 'manual'
            })
        return resultado