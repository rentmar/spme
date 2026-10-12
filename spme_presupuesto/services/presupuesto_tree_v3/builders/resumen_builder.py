# spme_presupuesto/services/presupuesto_tree_v3/builders/resumen_builder.py

from typing import Optional, List, Dict, Any, Union

from ..dto import TreeNodeV3
from ..base import BaseBuilderV3
from ..enums import TipoNodo, Profundidad
# from spme_presupuesto.repositories.presupuesto_tree_v3_repository import PresupuestoTreeV3Repository


class ResumenBuilderV3(BaseBuilderV3):
    """
    Builder para el nodo resumen (consolidado global).
    """
    
    def __init__(self, calculos, repository=None):
        super().__init__(calculos, repository)
    
    def get_tipo_nodo(self) -> str:
        return TipoNodo.RESUMEN.value
    
    def get_ids_by_parent(self, parent_id: int) -> List[int]:
        """Un resumen no tiene IDs."""
        return []
    
    def get_parent_id(self, id: int) -> Optional[int]:
        """Un resumen no tiene ID propio."""
        return None
    
    def build(
        self,
        proyecto_id: Optional[int] = None,
        nivel: int = 1,
        es_nodo_objetivo: bool = False,
        depth: Union[str, int] = Profundidad.ALL,
        nivel_nodo_objetivo: int = 0,
    ) -> TreeNodeV3:
        """
        Construye el nodo resumen.
        
        Flujo:
        1. Obtener datos del proyecto
        2. Obtener datos del contenedor de actividades (si se pasa)
        3. Consolidar planificación
        4. Consolidar ejecución
        5. Consolidar formularios
        6. Crear nodo resumen
        """
        if proyecto_id is None:
            raise ValueError("Se requiere un ID de proyecto para construir el resumen")

        proyecto_data = self.repository.obtener_proyecto(proyecto_id) if self.repository else {}
        planificacion_total = proyecto_data.get('presupuesto', 0.0) if proyecto_data else 0.0

        datos = {
            'nombre': 'Resumen Presupuestario',
            'planificacion': {
                'total': planificacion_total,
                'tiene_desglose': len(proyecto_data.get('desglose_financiadores', [])) > 0 if proyecto_data else False,
                'desglose_financiadores': proyecto_data.get('desglose_financiadores', []) if proyecto_data else [],
            },
            'ejecucion': {
                'total': 0.0,
                'porcentaje': 0.0,
            },
        }

        return TreeNodeV3(
            tipo_nodo=self.get_tipo_nodo(),
            id=None,
            nivel=nivel,
            es_nodo_virtual=True,
            es_contenedor=False,
            es_nodo_objetivo=es_nodo_objetivo,
            datos=datos,
            formularios=[],
            hijos=[],
        )



    def _consolidar_formularios_proyecto(self, proyecto_id: int) -> Dict[str, Any]:
        """
        Consolida todos los formularios del proyecto.
        
        Returns:
            Diccionario con totales y ejecutables.
        """
        # Obtener IDs de actividades
        actividades_ids = self.repository.obtener_actividades_proyecto(proyecto_id)
        
        formularios_list = []
        
        # Formularios directos de actividades
        for actividad_id in actividades_ids:
            formularios = self.repository.obtener_formularios_actividad(actividad_id)
            formularios_list.append(formularios)
            
            # Formularios de tareas
            tareas_ids = self.repository.obtener_tareas_actividad(actividad_id)
            for tarea_id in tareas_ids:
                formularios_tarea = self.repository.obtener_formularios_tarea(tarea_id)
                formularios_list.append(formularios_tarea)
        
        # Consolidar usando la clase de cálculos
        return self.calculos.consolidar_formularios(formularios_list)