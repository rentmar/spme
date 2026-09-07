# spme_presupuesto/services/presupuesto_tree_v3/builders/tarea_builder.py

from typing import Optional, List, Dict, Any

from ..dto import TreeNodeV3
from ..base import BaseBuilderV3
from spme_presupuesto.repositories.presupuesto_tree_v3_repository import PresupuestoTreeV3Repository


class TareaBuilderV3(BaseBuilderV3):
    """Builder para nodos de tipo 'tarea'."""
    
    def __init__(self, calculos):
        super().__init__(calculos)
        self.repository = PresupuestoTreeV3Repository()
    
    def get_tipo_nodo(self) -> str:
        return 'tarea'
    
    def get_ids_by_parent(self, parent_id: int) -> List[int]:
        """Obtiene IDs de tareas dado un ID de actividad."""
        return self.repository.obtener_tareas_actividad(parent_id)
    
    def get_parent_id(self, id: int) -> Optional[int]:
        """Obtiene el ID de la actividad padre."""
        return self.repository.obtener_actividad_de_tarea(id)
    
    def build(
        self,
        id: Optional[int] = None,
        nivel: int = 4,
        es_nodo_objetivo: bool = False,
    ) -> TreeNodeV3:
        """
        Construye un nodo de tipo tarea.
        """
        if id is None:
            raise ValueError("Se requiere un ID para construir una tarea")
        
        # 1. Obtener datos de la tarea
        tarea_data = self.repository.obtener_tarea(id)
        if not tarea_data:
            raise ValueError(f"Tarea con ID {id} no encontrada")
        
        # 2. Obtener formularios
        formularios = self.repository.obtener_formularios_tarea(id)
        
        # 3. Agregar flag a formularios
        formularios_con_flag = self._agregar_flag_formularios(formularios)
        
        # 4. Calcular ejecutado
        ejecutado_total = self._calcular_ejecutado(formularios)
        
        # 5. Calcular porcentaje
        planificacion_total = tarea_data.get('presupuesto', 0)
        porcentaje = self._calcular_porcentaje(ejecutado_total, planificacion_total)
        
        # 6. Obtener desglose y determinar si tiene desglose
        desglose_financiadores = tarea_data.get('desglose_financiadores', [])
        tiene_desglose = len(desglose_financiadores) > 0
        
        # 7. Construir datos del nodo
        datos = {
            'codigo': tarea_data.get('codigo'),
            'titulo': tarea_data.get('titulo'),
            'descripcion': tarea_data.get('descripcion'),
            'estado': tarea_data.get('estado'),
            'estado_display': tarea_data.get('estado_display'),
            'fecha_creacion': tarea_data.get('fecha_creacion'),
            'fecha_ejecucion': tarea_data.get('fecha_ejecucion'),
            'fecha_limite': tarea_data.get('fecha_limite'),
            'moneda': tarea_data.get('moneda'),
            'planificacion': {
                'total': planificacion_total,
                'tiene_desglose': tiene_desglose,
                'desglose_financiadores': desglose_financiadores,
            },
            'ejecucion': {
                'total': ejecutado_total,
                'porcentaje': porcentaje,
            },
        }
        
        # 8. Crear nodo
        nodo = TreeNodeV3(
            tipo_nodo=self.get_tipo_nodo(),
            id=id,
            nivel=nivel,
            es_nodo_virtual=False,
            es_contenedor=False,
            es_nodo_objetivo=es_nodo_objetivo,
            datos=datos,
            formularios=formularios_con_flag,
        )
        
        return nodo
    
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