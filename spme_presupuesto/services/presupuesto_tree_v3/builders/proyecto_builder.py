# spme_presupuesto/services/presupuesto_tree_v3/builders/proyecto_builder.py

from typing import Optional, List, Dict, Any

from ..dto import TreeNodeV3
from ..base import BaseBuilderV3
from spme_presupuesto.repositories.presupuesto_tree_v3_repository import PresupuestoTreeV3Repository
from .contenedor_actividades_builder import ContenedorActividadesBuilderV3
from .resumen_builder import ResumenBuilderV3


class ProyectoBuilderV3(BaseBuilderV3):
    """Builder para el nodo raíz 'proyecto'."""
    
    def __init__(self, calculos):
        super().__init__(calculos)
        self.repository = PresupuestoTreeV3Repository()
        self.contenedor_actividades_builder = ContenedorActividadesBuilderV3(calculos)
        self.resumen_builder = ResumenBuilderV3(calculos)
    
    def get_tipo_nodo(self) -> str:
        return 'proyecto'
    
    def get_ids_by_parent(self, parent_id: int) -> List[int]:
        """Un proyecto no tiene padre."""
        return []
    
    def get_parent_id(self, id: int) -> Optional[int]:
        """Un proyecto no tiene padre."""
        return None
    
    def build(
        self,
        id: Optional[int] = None,
        nivel: int = 0,
        es_nodo_objetivo: bool = True,
        incluir_tareas: bool = True,
    ) -> TreeNodeV3:
        """
        Construye el nodo raíz del árbol.
        
        Flujo:
        1. Obtener datos del proyecto
        2. Construir resumen
        3. Construir contenedor de actividades
        4. Calcular ejecutado total
        5. Calcular porcentaje
        6. Crear nodo proyecto
        """
        if id is None:
            raise ValueError("Se requiere un ID para construir el proyecto")
        
        # 1. Obtener datos del proyecto
        proyecto_data = self.repository.obtener_proyecto(id)
        if not proyecto_data:
            raise ValueError(f"Proyecto con ID {id} no encontrado")
        
        # 2. Construir contenedor de actividades
        contenedor_actividades = self.contenedor_actividades_builder.build(
            proyecto_id=id,
            nivel=nivel + 1,
            es_nodo_objetivo=False,
            incluir_tareas=incluir_tareas,
        )
        
        # 3. Construir resumen
        resumen = self.resumen_builder.build(
            proyecto_id=id,
            nivel=nivel + 1,
            es_nodo_objetivo=False,
            contenedor_actividades=contenedor_actividades,
        )
        
        # 4. Obtener datos de ejecución del resumen
        ejecucion_total = resumen.datos.get('ejecucion', {}).get('total', 0)
        porcentaje = resumen.datos.get('ejecucion', {}).get('porcentaje', 0)
        
        # 5. Obtener desglose de financiadores del proyecto
        desglose_financiadores = proyecto_data.get('desglose_financiadores', [])
        tiene_desglose = len(desglose_financiadores) > 0
        
        # 6. Construir datos del proyecto
        datos = {
            'codigo': proyecto_data.get('codigo'),
            'titulo': proyecto_data.get('titulo'),
            'descripcion': proyecto_data.get('descripcion'),
            'estado': proyecto_data.get('estado'),
            'estado_display': proyecto_data.get('estado_display'),
            'fecha_inicio': proyecto_data.get('fecha_inicio'),
            'fecha_finalizacion': proyecto_data.get('fecha_finalizacion'),
            'moneda': proyecto_data.get('moneda'),
            'planificacion': {
                'total': proyecto_data.get('presupuesto', 0),
                'tiene_desglose': tiene_desglose,
                'desglose_financiadores': desglose_financiadores,
                'actividades': resumen.datos.get('planificacion', {}).get('actividades', {}),
                'tareas': resumen.datos.get('planificacion', {}).get('tareas', {}),
            },
            'ejecucion': {
                'total': ejecucion_total,
                'porcentaje': porcentaje,
                'actividades': resumen.datos.get('ejecucion', {}).get('actividades', {}),
            },
        }
        
        # 7. Crear hijos
        hijos = [
            resumen,
            contenedor_actividades,
        ]
        
        # 8. Crear nodo proyecto
        nodo = TreeNodeV3(
            tipo_nodo=self.get_tipo_nodo(),
            id=id,
            nivel=nivel,
            es_nodo_virtual=False,
            es_contenedor=False,
            es_nodo_objetivo=es_nodo_objetivo,
            datos=datos,
            formularios=[],
            hijos=hijos,
        )
        
        return nodo