# spme_presupuesto/services/presupuesto_tree_v3/orchestrator.py

from typing import Optional, Union, Dict, Any

from .dto import TreeNodeV3, TreeMetadataV3, TreeResponseV3
from .depth_strategy import DepthStrategy
from .calculos import CalculosPresupuestariosV3
from .registry import PresupuestoRegistryV3
from .enums import TipoNodo, Direccion, Profundidad

from spme_presupuesto.repositories.presupuesto_tree_v3_repository import PresupuestoTreeV3Repository

from .builders.proyecto_builder import ProyectoBuilderV3
from .builders.actividad_builder import ActividadBuilderV3
from .builders.tarea_builder import TareaBuilderV3
from .builders.resumen_builder import ResumenBuilderV3
from .builders.contenedor_actividades_builder import ContenedorActividadesBuilderV3
from .builders.contenedor_tareas_builder import ContenedorTareasBuilderV3


class PresupuestoOrchestratorV3:
    """
    Orquestador para construir el árbol presupuestario V3.
    
    Coordina la construcción del árbol según los parámetros:
    - nodo: Tipo de nodo inicial ('proyecto', 'actividad', 'tarea', etc.)
    - id: ID del nodo
    - depth: Profundidad de expansión ('self', 'all', o entero)
    - direction: Dirección ('down', 'up', 'both')
    """

    def __init__(self, repository=None):
        self.repository = repository or PresupuestoTreeV3Repository()
        self.calculos = CalculosPresupuestariosV3()
        self.registry = PresupuestoRegistryV3()

        #Inicializar builders inyectando calculos y repositorios
        self.proyecto_builder = ProyectoBuilderV3(self.calculos, self.repository)
        self.actividad_builder = ActividadBuilderV3(self.calculos, self.repository)
        self.tarea_builder = TareaBuilderV3(self.calculos, self.repository)
        self.resumen_builder = ResumenBuilderV3(self.calculos, self.repository)
        self.contenedor_actividades_builder = ContenedorActividadesBuilderV3(self.calculos, self.repository)
        self.contenedor_tareas_builder = ContenedorTareasBuilderV3(self.calculos, self.repository)

        #Registrar builders en el registry
        self._registrar_builders()

    def _registrar_builders(self):
        """
        Registra los builders en el registry.
        """
        self.registry.register(
            tipo_nodo=TipoNodo.PROYECTO.value, 
            builder_class=ProyectoBuilderV3, 
            nivel=0
        )
        self.registry.register(
            tipo_nodo=TipoNodo.RESUMEN.value, 
            builder_class=ResumenBuilderV3, 
            nivel=1, 
            es_virtual=True
        )
        self.registry.register(
            tipo_nodo=TipoNodo.CONTENEDOR_ACTIVIDADES.value, 
            builder_class=ContenedorActividadesBuilderV3, 
            nivel=1, 
            es_virtual=True, 
            es_contenedor=True
        )
        self.registry.register(
            tipo_nodo=TipoNodo.ACTIVIDAD.value, 
            builder_class=ActividadBuilderV3, 
            nivel=2
        )
        self.registry.register(
            tipo_nodo=TipoNodo.CONTENEDOR_TAREAS.value, 
            builder_class=ContenedorTareasBuilderV3, 
            nivel=3, 
            es_virtual=True, 
            es_contenedor=True
        )
        self.registry.register(
            tipo_nodo=TipoNodo.TAREA.value, 
            builder_class=TareaBuilderV3, 
            nivel=4
        )

        # Registrar relaciones
        self.registry.register_children(TipoNodo.PROYECTO.value, [TipoNodo.RESUMEN.value, TipoNodo.CONTENEDOR_ACTIVIDADES.value])
        self.registry.register_children(TipoNodo.ACTIVIDAD.value, [TipoNodo.CONTENEDOR_TAREAS.value])
        self.registry.register_children(TipoNodo.RESUMEN.value, [])
        self.registry.register_children(TipoNodo.CONTENEDOR_ACTIVIDADES.value, [TipoNodo.ACTIVIDAD.value])
        self.registry.register_children(TipoNodo.CONTENEDOR_TAREAS.value, [TipoNodo.TAREA.value])
        self.registry.register_children(TipoNodo.TAREA.value, [])

    def build_tree(
        self,
        nodo: str,
        id: int,
        depth: Union[str, int] = Profundidad.ALL,
        direction: str = Direccion.DOWN.value,
    ) -> TreeResponseV3:
        """
        Construye el árbol completo con respuesta TreeResponseV3 y metadata.
        """
        # Normalizar strings
        nodo_str = str(nodo).lower()
        direction_str = str(direction).lower()
        # Validar tipo de nodo
        nodos_validos = [n.value for n in TipoNodo]
        if nodo_str not in nodos_validos:
            raise ValueError(f"Tipo de nodo inválido: {nodo}")
        # Validar dirección
        direcciones_validas = [d.value for d in Direccion]
        if direction_str not in direcciones_validas:
            raise ValueError(f"Dirección inválida: {direction}")
        # Construir árbol según dirección y nodo inicial
        arbol = self._build_nodo_inicial(nodo_str, id, depth, direction_str)
        
        # Calcular metadata
        metadata = self._build_metadata(arbol, nodo_str, id, depth, direction_str)
        
        return TreeResponseV3(arbol=arbol, metadata=metadata)

    def _build_nodo_inicial(
        self,
        nodo: str,
        id: int,
        depth: Union[str, int],
        direction: str,
    ) -> TreeNodeV3:
        """
        Construye el nodo inicial procesando navegación 'down', 'up' o 'both'.
        """
        # Mapeo de nivel inicial según el nodo objetivo
        nivel_map = {
            TipoNodo.PROYECTO.value: 0,
            TipoNodo.RESUMEN.value: 1,
            TipoNodo.CONTENEDOR_ACTIVIDADES.value: 1,
            TipoNodo.ACTIVIDAD.value: 2,
            TipoNodo.CONTENEDOR_TAREAS.value: 3,
            TipoNodo.TAREA.value: 4,
        }
        nivel_nodo_objetivo = nivel_map.get(nodo, 0)
        # A. Dirección DOWN (Construcción estándar descendente)
        if direction == Direccion.DOWN.value:
            if nodo == TipoNodo.PROYECTO.value:
                return self.proyecto_builder.build(id=id, nivel=0, es_nodo_objetivo=True, depth=depth, nivel_nodo_objetivo=0)
            elif nodo == TipoNodo.ACTIVIDAD.value:
                return self.actividad_builder.build(id=id, nivel=2, es_nodo_objetivo=True, depth=depth, nivel_nodo_objetivo=2)
            elif nodo == TipoNodo.TAREA.value:
                return self.tarea_builder.build(id=id, nivel=4, es_nodo_objetivo=True, depth=depth, nivel_nodo_objetivo=4)
            elif nodo == TipoNodo.CONTENEDOR_ACTIVIDADES.value:
                return self.contenedor_actividades_builder.build(proyecto_id=id, nivel=1, es_nodo_objetivo=True, depth=depth, nivel_nodo_objetivo=1)
            elif nodo == TipoNodo.CONTENEDOR_TAREAS.value:
                return self.contenedor_tareas_builder.build(actividad_id=id, nivel=3, es_nodo_objetivo=True, depth=depth, nivel_nodo_objetivo=3)
            elif nodo == TipoNodo.RESUMEN.value:
                return self.resumen_builder.build(proyecto_id=id, nivel=1, es_nodo_objetivo=True, depth=depth, nivel_nodo_objetivo=1)

        # B. Dirección UP o BOTH (Construcción ascendente de ancestros)
        else:
            depth_descendientes = depth if direction == Direccion.BOTH.value else Profundidad.SELF
            
            if nodo == TipoNodo.PROYECTO.value:
                return self.proyecto_builder.build(id=id, nivel=0, es_nodo_objetivo=True, depth=depth_descendientes, nivel_nodo_objetivo=0) 

            elif nodo == TipoNodo.ACTIVIDAD.value:
                proyecto_id = self.repository.obtener_proyecto_de_actividad(id)
                if not proyecto_id:
                    raise ValueError(f"No se encontró un proyecto padre para la Actividad ID {id}")

                proyecto_nodo = self.proyecto_builder.build(id=proyecto_id, nivel=0, es_nodo_objetivo=False, depth=1, nivel_nodo_objetivo=2)
                actividad_nodo = self.actividad_builder.build(id=id, nivel=2, es_nodo_objetivo=True, depth=depth_descendientes, nivel_nodo_objetivo=2)
                self._inyectar_actividad(proyecto_nodo, actividad_nodo)
                return proyecto_nodo
            elif nodo == TipoNodo.TAREA.value:
                actividad_id = self.repository.obtener_actividad_de_tarea(id)
                if not actividad_id:
                    raise ValueError(f"No se encontró una actividad padre para la Tarea ID {id}")

                proyecto_id = self.repository.obtener_proyecto_de_actividad(actividad_id)
                if not proyecto_id:
                    raise ValueError(f"No se encontró un proyecto padre para la Actividad ID {actividad_id}")

                proyecto_nodo = self.proyecto_builder.build(id=proyecto_id, nivel=0, es_nodo_objetivo=False, depth=1, nivel_nodo_objetivo=4)
                actividad_nodo = self.actividad_builder.build(id=actividad_id, nivel=2, es_nodo_objetivo=False, depth=1, nivel_nodo_objetivo=4)
                tarea_nodo = self.tarea_builder.build(id=id, nivel=4, es_nodo_objetivo=True, depth=depth_descendientes, nivel_nodo_objetivo=4)

                self._inyectar_tarea(actividad_nodo, tarea_nodo)
                self._inyectar_actividad(proyecto_nodo, actividad_nodo)
                return proyecto_nodo
            else:
                raise ValueError(f"Navegación {direction} no soportada para el nodo: {nodo}")

    def _inyectar_actividad(self, proyecto_nodo: TreeNodeV3, actividad_nodo: TreeNodeV3):
        for hijo in proyecto_nodo.hijos:
            if hijo.tipo_nodo == TipoNodo.CONTENEDOR_ACTIVIDADES.value:
                hijo.hijos = [act for act in hijo.hijos if act.id != actividad_nodo.id]
                hijo.hijos.append(actividad_nodo)
                break

    def _inyectar_tarea(self, actividad_nodo: TreeNodeV3, tarea_nodo: TreeNodeV3):
            for hijo in actividad_nodo.hijos:
                if hijo.tipo_nodo == TipoNodo.CONTENEDOR_TAREAS.value:
                    hijo.hijos = [t for t in hijo.hijos if t.id != tarea_nodo.id]
                    hijo.hijos.append(tarea_nodo)
                    break

    def _build_metadata(
                self,
                arbol: TreeNodeV3,
                nodo: str,
                id: int,
                depth: Union[str, int],
                direction: str,
        )->TreeMetadataV3:
            total_nodos = self._contar_nodos(arbol)
            profundidad_alcanzada = self._calcular_profundidad(arbol)
            
            return TreeMetadataV3(
                nodo_inicio=f"{nodo}:{id}",
                profundidad_solicitada=str(depth),
                profundidad_alcanzada=profundidad_alcanzada,
                total_nodos=total_nodos,
                direccion=direction,
            )

    def _contar_nodos(self, nodo: TreeNodeV3) -> int:
        total = 1
        for hijo in nodo.hijos:
            total += self._contar_nodos(hijo)
        return total

    def _calcular_profundidad(self, nodo: TreeNodeV3) -> int:
        if not nodo.hijos:
            return nodo.nivel
    
        profundidad_max = nodo.nivel
        for hijo in nodo.hijos:
            profundidad_hijo = self._calcular_profundidad(hijo)
            if profundidad_hijo > profundidad_max:
                profundidad_max = profundidad_hijo
        
        return profundidad_max

        
    