# spme/spme_presupuesto/services/presupuesto_tree/orchestrator.py
from typing import Union, Optional
from spme_presupuesto.services.presupuesto_tree.dto import TreeNode, TreeMetadata, TreeResponse, BuildContext
from spme_presupuesto.services.presupuesto_tree.registry import PresupuestoRegistry
from spme_presupuesto.services.presupuesto_tree.depth_strategy import DepthStrategy
from spme_presupuesto.services.presupuesto_tree.enums import NodeType, Direction

class PresupuestoOrchestrator:

    def __init__(self, registry: PresupuestoRegistry):
        self.registry = registry
        self.depth_strategy = DepthStrategy()
        self._total_nodos = 0

    def build_tree(
        self,
        nodo: str,
        id: int,
        depth: Union[str, int] = 'all',
        direction: str = 'down'
    ) -> TreeResponse:
        self._total_nodos = 0
        build_context = BuildContext()

        if nodo not in self.registry.get_registered_types():
            raise ValueError(f"Tipo de nodo '{nodo}' no registrado")

        if direction == Direction.DOWN.value:
            arbol = self._build_down(nodo, id, depth, build_context)
        elif direction == Direction.UP.value:
            arbol = self._build_up(nodo, id, depth, build_context)
        elif direction == Direction.BOTH.value:
            arbol = self._build_both(nodo, id, depth, build_context)
        else:
            raise ValueError(f"Dirección inválida: {direction}")

        metadata = self._build_metadata(nodo, id, depth, direction, arbol)
        return TreeResponse(arbol=arbol, metadata=metadata)

    # def _build_down(self, nodo, id, depth, build_context, nivel=0):
    #     builder = self.registry.get_builder(nodo)
    #     es_objetivo = (nivel == 0)
    #     current = builder.build(id, build_context, es_nodo_objetivo=es_objetivo, nivel=nivel)
    #     self._total_nodos += 1

    #     if self.depth_strategy.can_expand(nivel, depth):
    #         children_types = self.registry.get_children_types(nodo)
    #         for child_type in children_types:
    #             child_builder = self.registry.get_builder(child_type)
    #             child_ids = child_builder.get_ids_by_parent(id, nodo)
    #             for child_id in child_ids:
    #                 child_node = self._build_down(child_type, child_id, depth, build_context, nivel + 1)
    #                 current.hijos.append(child_node)

    #     return current

    def _build_up(self, nodo, id, depth, build_context, nivel=0):
        builder = self.registry.get_builder(nodo)
        es_objetivo = (nivel == 0)
        current = builder.build(id, build_context, es_nodo_objetivo=es_objetivo, nivel=nivel)
        self._total_nodos += 1

        if self.depth_strategy.can_expand(nivel, depth):
            parent_type = self.registry.get_parent_type(nodo)
            if parent_type:
                parent_builder = self.registry.get_builder(parent_type)
                parent_id = builder.get_parent_id(id, parent_type)
                if parent_id:
                    parent_node = self._build_up(parent_type, parent_id, depth, build_context, nivel + 1)
                    parent_node.hijos.append(current)
                    return parent_node

        return current

    def _build_both(self, nodo, id, depth, build_context):
        arbol = self._build_up(nodo, id, depth, build_context, nivel=0)
        nodo_objetivo = self._find_objetivo(arbol)
        if nodo_objetivo and self.depth_strategy.can_expand(0, depth):
            children_types = self.registry.get_children_types(nodo)
            for child_type in children_types:
                child_builder = self.registry.get_builder(child_type)
                child_ids = child_builder.get_ids_by_parent(id, nodo)
                for child_id in child_ids:
                    child_node = self._build_down(child_type, child_id, depth, build_context, nivel=1)
                    nodo_objetivo.hijos.append(child_node)
        return arbol

    def _find_objetivo(self, nodo):
        if nodo.es_nodo_objetivo:
            return nodo
        for hijo in nodo.hijos:
            result = self._find_objetivo(hijo)
            if result:
                return result
        return None

    def _build_metadata(self, nodo, id, depth, direction, arbol):
        profundidad_alcanzada = self._calculate_max_depth(arbol)
        return TreeMetadata(
            nodo_inicio=f"{nodo}:{id}",
            profundidad_solicitada=depth,
            profundidad_alcanzada=profundidad_alcanzada,
            total_nodos=self._total_nodos,
            direccion=direction,
            estructura=self.registry.get_estructura_texto(),
            actividades={'criterio_exclusion': "estado='CRD' O estaInactiva=true"}
        )

    def _calculate_max_depth(self, nodo, current_depth=0):
        if not nodo.hijos:
            return current_depth
        return max(self._calculate_max_depth(hijo, current_depth + 1) for hijo in nodo.hijos)

    def _build_down(self, nodo, id, depth, build_context, nivel=0):
        builder = self.registry.get_builder(nodo)
        es_objetivo = (nivel == 0)
        current = builder.build(id, build_context, es_nodo_objetivo=es_objetivo, nivel=nivel)
        self._total_nodos += 1

        if self.depth_strategy.can_expand(nivel, depth):
            children_types = self.registry.get_children_types(nodo)
            for child_type in children_types:
                child_builder = self.registry.get_builder(child_type)
                child_ids = child_builder.get_ids_by_parent(id, nodo)
                for child_id in child_ids:
                    child_node = self._build_down(child_type, child_id, depth, build_context, nivel + 1)
                    current.hijos.append(child_node)

        # Después de construir hijos, actualizar nodos virtuales
        if nodo == NodeType.PROYECTO.value:
            self._actualizar_resultados(current)

        return current

    def _actualizar_resultados(self, proyecto_nodo: TreeNode):
        """Actualiza los nodos virtuales con totales calculados."""
        actividades = []
        todas_tareas = []
        
        for hijo in proyecto_nodo.hijos:
            if hijo.tipo_nodo == NodeType.ACTIVIDAD.value:
                actividades.append(hijo)
                for nieto in hijo.hijos:
                    if nieto.tipo_nodo == NodeType.TAREA.value:
                        todas_tareas.append(nieto)
        
        # Actualizar resultado_actividades
        for hijo in proyecto_nodo.hijos:
            if hijo.tipo_nodo == NodeType.RESULTADO_ACTIVIDADES.value:
                total_presupuesto = sum(a.datos.get('presupuesto_actividad', 0) for a in actividades)
                total_ejecutado = sum(a.datos.get('presupuesto_ejecutado', 0) for a in actividades)
                
                hijo.datos['presupuesto_total'] = total_presupuesto
                hijo.datos['ejecutado_total'] = total_ejecutado
                hijo.datos['porcentaje_ejecucion_global'] = round(
                    (total_ejecutado / total_presupuesto * 100), 1
                ) if total_presupuesto > 0 else 0.0
                hijo.datos['cantidad_actividades'] = len(actividades)
            
            if hijo.tipo_nodo == NodeType.RESULTADO_TAREAS.value:
                total_presupuesto_tareas = sum(t.datos.get('presupuesto_tarea', 0) for t in todas_tareas)
                total_ejecutado_tareas = sum(t.datos.get('presupuesto_ejecutado', 0) for t in todas_tareas)
                
                hijo.datos['presupuesto_total_tareas'] = total_presupuesto_tareas
                hijo.datos['ejecutado_total_tareas'] = total_ejecutado_tareas
                hijo.datos['porcentaje_ejecucion_tareas'] = round(
                    (total_ejecutado_tareas / total_presupuesto_tareas * 100), 1
                ) if total_presupuesto_tareas > 0 else 0.0
                hijo.datos['cantidad_tareas'] = len(todas_tareas)