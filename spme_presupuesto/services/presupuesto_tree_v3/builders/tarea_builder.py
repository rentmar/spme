# spme_presupuesto/services/presupuesto_tree_v3/builders/tarea_builder.py

from typing import Optional, List, Dict, Any, Union

from ..dto import TreeNodeV3
from ..base import BaseBuilderV3
from ..enums import TipoNodo, Profundidad


class TareaBuilderV3(BaseBuilderV3):
    """Builder para nodos de tipo 'tarea'."""
    
    def __init__(self, calculos, repository=None):
        super().__init__(calculos, repository)
    
    def get_tipo_nodo(self) -> str:
        return TipoNodo.TAREA.value
    
    def get_ids_by_parent(self, parent_id: int) -> List[int]:
        """Obtiene IDs de tareas dado un ID de actividad."""
        if self.repository:
            return self.repository.obtener_tareas_actividad(parent_id)
        return []
    
    def get_parent_id(self, id: int) -> Optional[int]:
        """Obtiene el ID de la actividad padre."""
        if self.repository:
            return self.repository.obtener_actividad_de_tarea(id)
        return None
    
    def build(
        self,
        id: Optional[int] = None,
        nivel: int = 4,
        es_nodo_objetivo: bool = False,
        depth: Union[str, int] = Profundidad.ALL,
        nivel_nodo_objetivo: int = 0,
    ) -> TreeNodeV3:
        """
        Construye un nodo de tipo tarea.
        """
        if id is None:
            raise ValueError("Se requiere un ID para construir la tarea")
        tarea_data = self.repository.obtener_tarea(id) if self.repository else None
        if not tarea_data:
            raise ValueError(f"Tarea con ID {id} no encontrada")

        formularios = self.repository.obtener_formularios_tarea(id) if self.repository else []

        # Uso de CalculosPresupuestariosV3 con Decimal y la nueva regla ejecutable
        planificacion_total = tarea_data.get('presupuesto', 0.0)
        ejecucion_total = self.calculos.calcular_ejecutado_formularios(formularios)
        porcentaje = self._calcular_porcentaje(ejecucion_total, planificacion_total)

        datos = {
            'codigo': tarea_data.get('codigo'),
            'nombre': tarea_data.get('nombre'),
            'descripcion': tarea_data.get('descripcion'),
            'estado': tarea_data.get('estado'),
            'estado_display': tarea_data.get('estado_display'),
            'moneda': tarea_data.get('moneda', 'BOB'),
            'planificacion': {
                'total': planificacion_total,
                'tiene_desglose': len(tarea_data.get('desglose_financiadores', [])) > 0,
                'desglose_financiadores': tarea_data.get('desglose_financiadores', []),
            },
            'ejecucion': {
                'total': ejecucion_total,
                'porcentaje': porcentaje,
            },
        }

        return TreeNodeV3(
            tipo_nodo=self.get_tipo_nodo(),
            id=id,
            nivel=nivel,
            es_nodo_virtual=False,
            es_contenedor=False,
            es_nodo_objetivo=es_nodo_objetivo,
            datos=datos,
            formularios=formularios,
            hijos=[],
        )
        
    def _agregar_flag_formularios(self, formularios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Agrega flag cuenta_para_ejecutado a cada formulario."""
        for formulario in formularios:
            es_ejecutable = self.calculos.es_formulario_ejecutable(formulario)
            formulario['cuenta_para_ejecutado'] = es_ejecutable
            
            if not es_ejecutable:
                formulario['razon_exclusion'] = self._obtener_razon_exclusion(
                    formulario.get('tipo', ''),
                    formulario.get('estado', ''),
                )
        
        return formularios
    
    def _obtener_razon_exclusion(self, tipo: str, estado: str) -> str:
        """Obtiene la razón por la cual un formulario no cuenta para ejecutado."""
        tipos_ejecutables = {'rendicion_cuentas', 'solicitud_reembolso'}
        
        if tipo not in tipos_ejecutables:
            return 'Tipo no ejecutable'
        
        if estado != 'aprobado':
            return 'Estado no aprobado'
        
        return 'No especificada'