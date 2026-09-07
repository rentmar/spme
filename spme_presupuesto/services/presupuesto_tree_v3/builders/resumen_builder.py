# spme_presupuesto/services/presupuesto_tree_v3/builders/resumen_builder.py

from typing import Optional, List, Dict, Any

from ..dto import TreeNodeV3
from ..base import BaseBuilderV3
from spme_presupuesto.repositories.presupuesto_tree_v3_repository import PresupuestoTreeV3Repository


class ResumenBuilderV3(BaseBuilderV3):
    """Builder para el nodo resumen (consolidado global)."""
    
    def __init__(self, calculos):
        super().__init__(calculos)
        self.repository = PresupuestoTreeV3Repository()
    
    def get_tipo_nodo(self) -> str:
        return 'resumen'
    
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
        contenedor_actividades: Optional[TreeNodeV3] = None,
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
        
        # 1. Obtener datos del proyecto
        proyecto_data = self.repository.obtener_proyecto(proyecto_id)
        if not proyecto_data:
            raise ValueError(f"Proyecto con ID {proyecto_id} no encontrado")
        
        # 2. Obtener datos del contenedor de actividades
        planificacion_actividades = 0.0
        planificacion_tareas = 0.0
        ejecucion_directo = 0.0
        ejecucion_tareas = 0.0
        ejecucion_total = 0.0
        cantidad_actividades = 0
        cantidad_tareas = 0
        desglose_financiadores = []
        
        if contenedor_actividades:
            datos_contenedor = contenedor_actividades.datos
            planificacion_actividades = datos_contenedor.get('planificacion', {}).get('total', 0)
            planificacion_tareas = datos_contenedor.get('planificacion', {}).get('tareas', {}).get('total', 0)
            ejecucion_directo = datos_contenedor.get('ejecucion', {}).get('directo', 0)
            ejecucion_tareas = datos_contenedor.get('ejecucion', {}).get('tareas', 0)
            ejecucion_total = datos_contenedor.get('ejecucion', {}).get('total', 0)
            cantidad_actividades = datos_contenedor.get('cantidad', 0)
            cantidad_tareas = datos_contenedor.get('planificacion', {}).get('tareas', {}).get('cantidad', 0)
            desglose_financiadores = datos_contenedor.get('planificacion', {}).get('desglose_financiadores', [])
        
        # 3. Obtener presupuesto total del proyecto
        planificacion_total = proyecto_data.get('presupuesto', 0)
        
        # 4. Calcular porcentaje
        porcentaje = self._calcular_porcentaje(ejecucion_total, planificacion_total)
        
        # 5. Consolidar formularios
        formularios_consolidados = self._consolidar_formularios_proyecto(proyecto_id)
        
        # 6. Construir datos del resumen
        datos = {
            'nombre': 'Resumen',
            'planificacion': {
                'total': planificacion_total,
                'actividades': {
                    'cantidad': cantidad_actividades,
                    'total': planificacion_actividades,
                },
                'tareas': {
                    'cantidad': cantidad_tareas,
                    'total': planificacion_tareas,
                },
                'tiene_desglose': len(desglose_financiadores) > 0,
                'desglose_financiadores': desglose_financiadores,
            },
            'ejecucion': {
                'total': ejecucion_total,
                'porcentaje': porcentaje,
                'actividades': {
                    'total': ejecucion_total,
                    'directo': ejecucion_directo,
                    'tareas': ejecucion_tareas,
                },
            },
            'formularios_consolidados': formularios_consolidados,
        }
        
        # 7. Crear nodo resumen
        nodo = TreeNodeV3(
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
        
        return nodo
    
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