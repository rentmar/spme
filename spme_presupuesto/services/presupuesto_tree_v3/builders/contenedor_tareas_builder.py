# spme_presupuesto/services/presupuesto_tree_v3/builders/contenedor_tareas_builder.py

from typing import Optional, List, Dict, Any

from ..dto import TreeNodeV3
from ..base import BaseBuilderV3
from spme_presupuesto.repositories.presupuesto_tree_v3_repository import PresupuestoTreeV3Repository
from .tarea_builder import TareaBuilderV3


class ContenedorTareasBuilderV3(BaseBuilderV3):
    """Builder para el contenedor de tareas de una actividad."""
    
    def __init__(self, calculos):
        super().__init__(calculos)
        self.repository = PresupuestoTreeV3Repository()
        self.tarea_builder = TareaBuilderV3(calculos)
    
    def get_tipo_nodo(self) -> str:
        return 'contenedor_tareas'
    
    def get_ids_by_parent(self, parent_id: int) -> List[int]:
        """Un contenedor no tiene IDs, se accede por actividad padre."""
        return []
    
    def get_parent_id(self, id: int) -> Optional[int]:
        """Un contenedor no tiene ID propio."""
        return None
    
    def build(
        self,
        actividad_id: Optional[int] = None,
        nivel: int = 3,
        es_nodo_objetivo: bool = False,
    ) -> TreeNodeV3:
        """
        Construye el contenedor de tareas de una actividad.
        
        Flujo:
        1. Obtener IDs de tareas de la actividad
        2. Construir cada tarea
        3. Consolidar totales de planificación
        4. Consolidar totales de ejecución
        5. Crear nodo contenedor
        """
        if actividad_id is None:
            raise ValueError("Se requiere un ID de actividad para construir el contenedor de tareas")
        
        # 1. Obtener IDs de tareas
        tareas_ids = self.repository.obtener_tareas_actividad(actividad_id)
        
        # 2. Construir cada tarea
        tareas_nodos = []
        for tarea_id in tareas_ids:
            try:
                tarea_nodo = self.tarea_builder.build(
                    id=tarea_id,
                    nivel=nivel + 1,  # Las tareas están un nivel más abajo
                    es_nodo_objetivo=False,
                )
                tareas_nodos.append(tarea_nodo)
            except ValueError as e:
                # Si una tarea no existe, la omitimos
                continue
        
        # 3. Consolidar planificación
        planificacion_total = sum(
            tarea.datos.get('planificacion', {}).get('total', 0)
            for tarea in tareas_nodos
        )
        
        # 4. Consolidar ejecución
        ejecucion_total = sum(
            tarea.datos.get('ejecucion', {}).get('total', 0)
            for tarea in tareas_nodos
        )
        
        # 5. Calcular porcentaje
        porcentaje = self._calcular_porcentaje(ejecucion_total, planificacion_total)
        
        # 6. Consolidar desglose de financiadores
        desglose_financiadores = self._consolidar_desglose_tareas(tareas_nodos)
        tiene_desglose = len(desglose_financiadores) > 0
        
        # 7. Construir datos del contenedor
        datos = {
            'nombre': 'Tareas',
            'cantidad': len(tareas_nodos),
            'planificacion': {
                'total': planificacion_total,
                'tiene_desglose': tiene_desglose,
                'desglose_financiadores': desglose_financiadores,
            },
            'ejecucion': {
                'total': ejecucion_total,
                'porcentaje': porcentaje,
            },
        }
        
        # 8. Crear nodo contenedor
        nodo = TreeNodeV3(
            tipo_nodo=self.get_tipo_nodo(),
            id=None,
            nivel=nivel,
            es_nodo_virtual=True,
            es_contenedor=True,
            es_nodo_objetivo=es_nodo_objetivo,
            datos=datos,
            formularios=[],
            hijos=tareas_nodos,
        )
        
        return nodo
    
    def _consolidar_desglose_tareas(self, tareas_nodos: List[TreeNodeV3]) -> List[Dict[str, Any]]:
        """
        Consolida el desglose de financiadores de todas las tareas.
        
        Args:
            tareas_nodos: Lista de nodos de tareas.
        
        Returns:
            Lista consolidada de financiadores.
        """
        consolidado: Dict[str, Dict[str, Any]] = {}
        
        for tarea in tareas_nodos:
            desglose = tarea.datos.get('planificacion', {}).get('desglose_financiadores', [])
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