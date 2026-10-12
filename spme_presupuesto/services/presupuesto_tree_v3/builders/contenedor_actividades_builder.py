# spme_presupuesto/services/presupuesto_tree_v3/builders/contenedor_actividades_builder.py

from typing import Optional, List, Dict, Any, Union

from ..dto import TreeNodeV3
from ..base import BaseBuilderV3
from ..depth_strategy import DepthStrategy
from ..enums import TipoNodo, Profundidad
from .actividad_builder import ActividadBuilderV3



class ContenedorActividadesBuilderV3(BaseBuilderV3):
    """Builder para el contenedor de actividades de un proyecto."""
    
    def __init__(self, calculos, repository=None):
        super().__init__(calculos, repository)
        self.actividad_builder = ActividadBuilderV3(calculos, repository)
    
    def get_tipo_nodo(self) -> str:
        return TipoNodo.CONTENEDOR_ACTIVIDADES.value 
    
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
        depth: Union[str, int] = Profundidad.ALL,
        nivel_nodo_objetivo: int = 0,
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
            raise ValueError("Se requiere un ID de proyecto para el contenedor de actividades")

        actividades_ids = self.repository.obtener_actividades_proyecto(proyecto_id) if self.repository else []
        actividades_nodos = []
        nivel_hijos = nivel + 1  # Nivel 2

        if DepthStrategy.can_expand(nivel_nodo_objetivo, nivel_hijos, depth):
            for act_id in actividades_ids:
                try:
                    act_nodo = self.actividad_builder.build(
                        id=act_id,
                        nivel=nivel_hijos,
                        es_nodo_objetivo=False,
                        depth=depth,
                        nivel_nodo_objetivo=nivel_nodo_objetivo,
                    )
                    actividades_nodos.append(act_nodo)
                except Exception:
                    continue

        planificacion_total = sum(
            act.datos.get('planificacion', {}).get('total', 0.0) for act in actividades_nodos
        )
        ejecucion_total = sum(
            act.datos.get('ejecucion', {}).get('total', 0.0) for act in actividades_nodos
        )
        porcentaje = self._calcular_porcentaje(ejecucion_total, planificacion_total)

        desgloses_actividades = [
            act.datos.get('planificacion', {}).get('desglose_financiadores', [])
            for act in actividades_nodos
        ]
        desglose_financiadores = self.calculos.consolidar_por_financiador(desgloses_actividades)

        datos = {
            'nombre': 'Actividades',
            'cantidad': len(actividades_ids),
            'planificacion': {
                'total': planificacion_total,
                'tiene_desglose': len(desglose_financiadores) > 0,
                'desglose_financiadores': desglose_financiadores,
            },
            'ejecucion': {
                'total': ejecucion_total,
                'porcentaje': porcentaje,
            },
        }

        return TreeNodeV3(
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