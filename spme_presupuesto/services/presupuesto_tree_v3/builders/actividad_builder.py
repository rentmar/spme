# spme_presupuesto/services/presupuesto_tree_v3/builders/actividad_builder.py

from typing import Optional, List, Dict, Any

from ..dto import TreeNodeV3
from ..base import BaseBuilderV3
from spme_presupuesto.repositories.presupuesto_tree_v3_repository import PresupuestoTreeV3Repository
from .contenedor_tareas_builder import ContenedorTareasBuilderV3


class ActividadBuilderV3(BaseBuilderV3):
    """Builder para nodos de tipo 'actividad'."""
    
    def __init__(self, calculos):
        super().__init__(calculos)
        self.repository = PresupuestoTreeV3Repository()
        self.contenedor_tareas_builder = ContenedorTareasBuilderV3(calculos)
    
    def get_tipo_nodo(self) -> str:
        return 'actividad'
    
    def get_ids_by_parent(self, parent_id: int) -> List[int]:
        """Obtiene IDs de actividades dado un ID de proyecto."""
        return self.repository.obtener_actividades_proyecto(parent_id)
    
    def get_parent_id(self, id: int) -> Optional[int]:
        """Obtiene el ID del proyecto padre."""
        return self.repository.obtener_proyecto_de_actividad(id)
    
    def build(
        self,
        id: Optional[int] = None,
        nivel: int = 2,
        es_nodo_objetivo: bool = False,
        incluir_tareas: bool = True,
    ) -> TreeNodeV3:
        """
        Construye un nodo de tipo actividad.
        """
        if id is None:
            raise ValueError("Se requiere un ID para construir una actividad")
        
        # 1. Obtener datos de la actividad
        actividad_data = self.repository.obtener_actividad(id)
        if not actividad_data:
            raise ValueError(f"Actividad con ID {id} no encontrada")
        
        # 2. Obtener formularios directos
        formularios = self.repository.obtener_formularios_actividad(id)
        
        # 3. Agregar flag a formularios
        formularios_con_flag = self._agregar_flag_formularios(formularios)
        
        # 4. Calcular ejecutado directo
        ejecutado_directo = self._calcular_ejecutado(formularios)
        
        # 5. Construir contenedor de tareas
        ejecutado_tareas = 0.0
        planificacion_tareas = 0.0
        contenedor_tareas = None
        
        if incluir_tareas:
            try:
                contenedor_tareas = self.contenedor_tareas_builder.build(
                    actividad_id=id,
                    nivel=nivel + 1,
                    es_nodo_objetivo=False,
                )
                ejecutado_tareas = contenedor_tareas.datos.get('ejecucion', {}).get('total', 0)
                planificacion_tareas = contenedor_tareas.datos.get('planificacion', {}).get('total', 0)
            except ValueError:
                contenedor_tareas = None
        
        # 6. Calcular ejecutado total
        ejecutado_total = ejecutado_directo + ejecutado_tareas
        
        # 7. Calcular porcentaje
        planificacion_total = actividad_data.get('presupuesto', 0)
        porcentaje = self._calcular_porcentaje(ejecutado_total, planificacion_total)
        
        # 8. Obtener desglose
        desglose_financiadores = actividad_data.get('desglose_financiadores', [])
        tiene_desglose = len(desglose_financiadores) > 0
        
        # 9. Construir datos del nodo
        datos = {
            'codigo': actividad_data.get('codigo'),
            'nombre': actividad_data.get('nombre'),
            'descripcion': actividad_data.get('descripcion'),
            'estado': actividad_data.get('estado'),
            'estado_display': actividad_data.get('estado_display'),
            'fecha_inicio': actividad_data.get('fecha_inicio'),
            'fecha_cierre': actividad_data.get('fecha_cierre'),
            'responsable': actividad_data.get('responsable'),
            'moneda': actividad_data.get('moneda'),
            'planificacion': {
                'total': planificacion_total,
                'tiene_desglose': tiene_desglose,
                'desglose_financiadores': desglose_financiadores,
                'tareas': {
                    'total': planificacion_tareas,
                    'cantidad': len(contenedor_tareas.hijos) if contenedor_tareas else 0,
                },
            },
            'ejecucion': {
                'directo': ejecutado_directo,
                'tareas': ejecutado_tareas,
                'total': ejecutado_total,
                'porcentaje': porcentaje,
            },
        }
        
        # 10. Crear hijos
        hijos = []
        if contenedor_tareas:
            hijos.append(contenedor_tareas)
        
        # 11. Crear nodo
        nodo = TreeNodeV3(
            tipo_nodo=self.get_tipo_nodo(),
            id=id,
            nivel=nivel,
            es_nodo_virtual=False,
            es_contenedor=False,
            es_nodo_objetivo=es_nodo_objetivo,
            datos=datos,
            formularios=formularios_con_flag,
            hijos=hijos,
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