# spme_presupuesto/services/presupuesto_tree_v3/builders/contenedor_actividades_builder.py

from typing import Optional, List, Dict, Any

from ..dto import TreeNodeV3
from ..base import BaseBuilderV3
from spme_presupuesto.repositories.presupuesto_tree_v3_repository import PresupuestoTreeV3Repository
from .actividad_builder import ActividadBuilderV3


class ContenedorActividadesBuilderV3(BaseBuilderV3):
    """Builder para el contenedor de actividades de un proyecto."""
    
    def __init__(self, calculos):
        super().__init__(calculos)
        self.repository = PresupuestoTreeV3Repository()
        self.actividad_builder = ActividadBuilderV3(calculos)
    
    def get_tipo_nodo(self) -> str:
        return 'contenedor_actividades'
    
    def get_ids_by_parent(self, parent_id: int) -> List[int]:
        """Un contenedor no tiene IDs, se accede por proyecto padre."""
        return []
    
    def get_parent_id(self, id: int) -> Optional[int]:
        """Un contenedor no tiene ID propio."""
        return None
    
    def build(
        self,
        proyecto_id: Optional[int] = None,
        nivel: int = 1,
        es_nodo_objetivo: bool = False,
        incluir_tareas: bool = True,
    ) -> TreeNodeV3:
        """
        Construye el contenedor de actividades de un proyecto.
        
        Flujo:
        1. Obtener IDs de actividades del proyecto
        2. Construir cada actividad
        3. Consolidar totales de planificación
        4. Consolidar totales de ejecución
        5. Consolidar desglose de financiadores
        6. Crear nodo contenedor
        """
        if proyecto_id is None:
            raise ValueError("Se requiere un ID de proyecto para construir el contenedor de actividades")
        
        # 1. Obtener IDs de actividades
        actividades_ids = self.repository.obtener_actividades_proyecto(proyecto_id)
        
        # 2. Construir cada actividad
        actividades_nodos = []
        for actividad_id in actividades_ids:
            try:
                actividad_nodo = self.actividad_builder.build(
                    id=actividad_id,
                    nivel=nivel + 1,  # Las actividades están un nivel más abajo
                    es_nodo_objetivo=False,
                    incluir_tareas=incluir_tareas,
                )
                actividades_nodos.append(actividad_nodo)
            except ValueError as e:
                # Si una actividad no existe, la omitimos
                continue
        
        # 3. Consolidar planificación
        planificacion_total = sum(
            actividad.datos.get('planificacion', {}).get('total', 0)
            for actividad in actividades_nodos
        )
        
        # 4. Consolidar ejecución
        ejecucion_total = sum(
            actividad.datos.get('ejecucion', {}).get('total', 0)
            for actividad in actividades_nodos
        )
        
        ejecucion_directo = sum(
            actividad.datos.get('ejecucion', {}).get('directo', 0)
            for actividad in actividades_nodos
        )
        
        ejecucion_tareas = sum(
            actividad.datos.get('ejecucion', {}).get('tareas', 0)
            for actividad in actividades_nodos
        )
        
        # 5. Calcular porcentaje
        porcentaje = self._calcular_porcentaje(ejecucion_total, planificacion_total)
        
        # 6. Consolidar desglose de financiadores
        desglose_financiadores = self._consolidar_desglose_actividades(actividades_nodos)
        tiene_desglose = len(desglose_financiadores) > 0
        
        # 7. Consolidar tareas
        tareas_cantidad = sum(
            actividad.datos.get('planificacion', {}).get('tareas', {}).get('cantidad', 0)
            for actividad in actividades_nodos
        )
        
        tareas_planificacion = sum(
            actividad.datos.get('planificacion', {}).get('tareas', {}).get('total', 0)
            for actividad in actividades_nodos
        )
        
        # 8. Construir datos del contenedor
        datos = {
            'nombre': 'Actividades',
            'cantidad': len(actividades_nodos),
            'planificacion': {
                'total': planificacion_total,
                'tiene_desglose': tiene_desglose,
                'desglose_financiadores': desglose_financiadores,
                'tareas': {
                    'total': tareas_planificacion,
                    'cantidad': tareas_cantidad,
                },
            },
            'ejecucion': {
                'directo': ejecucion_directo,
                'tareas': ejecucion_tareas,
                'total': ejecucion_total,
                'porcentaje': porcentaje,
            },
        }
        
        # 9. Crear nodo contenedor
        nodo = TreeNodeV3(
            tipo_nodo=self.get_tipo_nodo(),
            id=None,
            nivel=nivel,
            es_nodo_virtual=True,
            es_contenedor=True,
            es_nodo_objetivo=es_nodo_objetivo,
            datos=datos,
            formularios=[],
            hijos=actividades_nodos,
        )
        
        return nodo
    
    def _consolidar_desglose_actividades(self, actividades_nodos: List[TreeNodeV3]) -> List[Dict[str, Any]]:
        """
        Consolida el desglose de financiadores de todas las actividades.
        
        Args:
            actividades_nodos: Lista de nodos de actividades.
        
        Returns:
            Lista consolidada de financiadores.
        """
        consolidado: Dict[str, Dict[str, Any]] = {}
        
        for actividad in actividades_nodos:
            desglose = actividad.datos.get('planificacion', {}).get('desglose_financiadores', [])
            for financiador in desglose:
                nombre = financiador.get('nombre', '')
                monto = float(financiador.get('monto', 0))
                
                if nombre not in consolidado:
                    consolidado[nombre] = {
                        'nombre': nombre,
                        'monto': 0.0,
                    }
                    if 'id' in financiador:
                        consolidado[nombre]['id'] = financiador['id']
                    if 'es_existente' in financiador:
                        consolidado[nombre]['es_existente'] = financiador['es_existente']
                    if 'tipo' in financiador:
                        consolidado[nombre]['tipo'] = financiador['tipo']
                
                consolidado[nombre]['monto'] += monto
        
        return list(consolidado.values())