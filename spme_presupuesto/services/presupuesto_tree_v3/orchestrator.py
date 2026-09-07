# spme_presupuesto/services/presupuesto_tree_v3/orchestrator.py

from typing import Optional, Union, Dict, Any

from .dto import TreeNodeV3, TreeMetadataV3, TreeResponseV3
from .depth_strategy import DepthStrategy
from .calculos import CalculosPresupuestariosV3
from .registry import PresupuestoRegistryV3
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
    - nodo: Tipo de nodo inicial
    - id: ID del nodo
    - depth: Profundidad de expansión
    - direction: Dirección (down, up, both)
    """
    
    def __init__(self):
        self.calculos = CalculosPresupuestariosV3()
        self.registry = PresupuestoRegistryV3()
        
        # Inicializar builders
        self.proyecto_builder = ProyectoBuilderV3(self.calculos)
        self.actividad_builder = ActividadBuilderV3(self.calculos)
        self.tarea_builder = TareaBuilderV3(self.calculos)
        self.resumen_builder = ResumenBuilderV3(self.calculos)
        self.contenedor_actividades_builder = ContenedorActividadesBuilderV3(self.calculos)
        self.contenedor_tareas_builder = ContenedorTareasBuilderV3(self.calculos)
        
        # Registrar builders en el registry
        self._registrar_builders()
    
    def _registrar_builders(self):
        """Registra los builders en el registry."""
        self.registry.register('proyecto', ProyectoBuilderV3, nivel=0)
        self.registry.register('resumen', ResumenBuilderV3, nivel=1, es_virtual=True)
        self.registry.register('contenedor_actividades', ContenedorActividadesBuilderV3, nivel=1, es_virtual=True, es_contenedor=True)
        self.registry.register('actividad', ActividadBuilderV3, nivel=2)
        self.registry.register('contenedor_tareas', ContenedorTareasBuilderV3, nivel=3, es_virtual=True, es_contenedor=True)
        self.registry.register('tarea', TareaBuilderV3, nivel=4)
        
        # Registrar relaciones
        self.registry.register_children('proyecto', ['resumen', 'contenedor_actividades'])
        self.registry.register_children('actividad', ['contenedor_tareas'])
        self.registry.register_children('resumen', [])
        self.registry.register_children('contenedor_actividades', ['actividad'])
        self.registry.register_children('contenedor_tareas', ['tarea'])
        self.registry.register_children('tarea', [])
    
    def build_tree(
        self,
        nodo: str,
        id: int,
        depth: Union[str, int] = 'all',
        direction: str = 'down',
    ) -> TreeResponseV3:
        """
        Construye el árbol completo.
        
        Args:
            nodo: Tipo de nodo inicial ('proyecto', 'actividad', 'tarea', etc.)
            id: ID del nodo
            depth: Profundidad ('self', 'all', o número)
            direction: Dirección ('down', 'up', 'both')
        
        Returns:
            TreeResponseV3 con el árbol y metadata.
        """
        # Validar nodo
        if nodo not in ['proyecto', 'actividad', 'tarea', 'resumen', 'contenedor_actividades', 'contenedor_tareas']:
            raise ValueError(f"Tipo de nodo inválido: {nodo}")
        
        # Validar dirección
        if direction not in ['down', 'up', 'both']:
            raise ValueError(f"Dirección inválida: {direction}")
        
        # Construir árbol según el nodo inicial
        arbol = self._build_nodo_inicial(nodo, id, depth, direction)
        
        # Calcular metadata
        metadata = self._build_metadata(arbol, nodo, id, depth, direction)
        
        return TreeResponseV3(arbol=arbol, metadata=metadata)
    
    def _build_nodo_inicial(
        self,
        nodo: str,
        id: int,
        depth: Union[str, int],
        direction: str,
    ) -> TreeNodeV3:
        """
        Construye el nodo inicial del árbol.
        """
        if nodo == 'proyecto':
            return self.proyecto_builder.build(
                id=id,
                nivel=0,
                es_nodo_objetivo=True,
            )
        
        elif nodo == 'actividad':
            return self.actividad_builder.build(
                id=id,
                nivel=2,
                es_nodo_objetivo=True,
            )
        
        elif nodo == 'tarea':
            return self.tarea_builder.build(
                id=id,
                nivel=4,
                es_nodo_objetivo=True,
            )
        
        elif nodo == 'contenedor_tareas':
            return self.contenedor_tareas_builder.build(
                actividad_id=id,
                nivel=3,
                es_nodo_objetivo=True,
            )
        
        elif nodo == 'contenedor_actividades':
            return self.contenedor_actividades_builder.build(
                proyecto_id=id,
                nivel=1,
                es_nodo_objetivo=True,
            )
        
        elif nodo == 'resumen':
            # Para resumen necesitamos el proyecto_id
            return self.resumen_builder.build(
                proyecto_id=id,
                nivel=1,
                es_nodo_objetivo=True,
            )
        
        else:
            raise ValueError(f"Nodo no soportado: {nodo}")
    
    def _build_metadata(
        self,
        arbol: TreeNodeV3,
        nodo: str,
        id: int,
        depth: Union[str, int],
        direction: str,
    ) -> TreeMetadataV3:
        """
        Construye la metadata del árbol.
        """
        # Calcular total de nodos
        total_nodos = self._contar_nodos(arbol)
        
        # Calcular profundidad alcanzada
        profundidad_alcanzada = self._calcular_profundidad(arbol)
        
        return TreeMetadataV3(
            nodo_inicio=f"{nodo}:{id}",
            profundidad_solicitada=str(depth),
            profundidad_alcanzada=profundidad_alcanzada,
            total_nodos=total_nodos,
            direccion=direction,
        )
    
    def _contar_nodos(self, nodo: TreeNodeV3) -> int:
        """Cuenta el total de nodos en el árbol."""
        total = 1  # El nodo actual
        
        for hijo in nodo.hijos:
            total += self._contar_nodos(hijo)
        
        return total
    
    def _calcular_profundidad(self, nodo: TreeNodeV3) -> int:
        """Calcula la profundidad máxima del árbol."""
        if not nodo.hijos:
            return nodo.nivel
        
        profundidad_max = nodo.nivel
        
        for hijo in nodo.hijos:
            profundidad_hijo = self._calcular_profundidad(hijo)
            if profundidad_hijo > profundidad_max:
                profundidad_max = profundidad_hijo
        
        return profundidad_max