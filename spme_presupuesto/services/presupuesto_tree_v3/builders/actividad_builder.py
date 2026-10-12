# spme_presupuesto/services/presupuesto_tree_v3/builders/actividad_builder.py

from typing import Optional, List, Dict, Any, Union

from ..dto import TreeNodeV3
from ..base import BaseBuilderV3
from ..depth_strategy import DepthStrategy
from ..enums import TipoNodo, Profundidad
from .contenedor_tareas_builder import ContenedorTareasBuilderV3


class ActividadBuilderV3(BaseBuilderV3):
    """Builder para nodos de tipo 'actividad'."""
    
    def __init__(self, calculos, repository=None):
        super().__init__(calculos, repository)
        self.contenedor_tareas_builder = ContenedorTareasBuilderV3(calculos, repository)
    
    def get_tipo_nodo(self) -> str:
        return TipoNodo.ACTIVIDAD.value
    
    def get_ids_by_parent(self, parent_id: int) -> List[int]:
        """Obtiene IDs de actividades dado un ID de proyecto."""
        if self.repository:
            return self.repository.obtener_actividades_proyecto(parent_id)
        return []
    
    def get_parent_id(self, id: int) -> Optional[int]:
        """Obtiene el ID del proyecto padre."""
        if self.repository:
            return self.repository.obtener_proyecto_de_actividad(id)
        return None

    
    def build(
        self,
        id: Optional[int] = None,
        nivel: int = 2,
        es_nodo_objetivo: bool = False,
        depth: Union[str, int] = Profundidad.ALL,
        nivel_nodo_objetivo: int = 0,
    ) -> TreeNodeV3:
        """
        Construye un nodo de tipo actividad.
        """
        if id is None:
            raise ValueError("Se requiere un ID para construir la actividad")

    
        # 1. Obtener datos de la actividad
        actividad_data = self.repository.obtener_actividad(id) if self.repository else None
        if not actividad_data:
            raise ValueError(f"Actividad con ID {id} no encontrada")
        hijos = []
        nivel_hijos = nivel + 1  # Nivel 3 (Contenedor de Tareas)

        if DepthStrategy.can_expand(nivel_nodo_objetivo, nivel_hijos, depth):
            try:
                contenedor_nodo = self.contenedor_tareas_builder.build(
                    actividad_id=id,
                    nivel=nivel_hijos,
                    es_nodo_objetivo=False,
                    depth=depth,
                    nivel_nodo_objetivo=nivel_nodo_objetivo,
                )
                hijos.append(contenedor_nodo)
            except Exception:
                pass

        planificacion_total = actividad_data.get('presupuesto', 0.0)
        ejecucion_total = sum(
            hijo.datos.get('ejecucion', {}).get('total', 0.0) for hijo in hijos
        )
        porcentaje = self._calcular_porcentaje(ejecucion_total, planificacion_total)

        datos = {
            'codigo': actividad_data.get('codigo'),
            'nombre': actividad_data.get('nombre'),
            'descripcion': actividad_data.get('descripcion'),
            'estado': actividad_data.get('estado'),
            'estado_display': actividad_data.get('estado_display'),
            'responsable': actividad_data.get('responsable'),
            'moneda': actividad_data.get('moneda', 'BOB'),
            'planificacion': {
                'total': planificacion_total,
                'tiene_desglose': len(actividad_data.get('desglose_financiadores', [])) > 0,
                'desglose_financiadores': actividad_data.get('desglose_financiadores', []),
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
            formularios=[],
            hijos=hijos,
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