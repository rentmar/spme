# spme_presupuesto/services/presupuesto_tree_v3/builders/proyecto_builder.py
# spme_presupuesto/services/presupuesto_tree_v3/builders/proyecto_builder.py

from typing import Optional, List, Dict, Any, Union

from ..dto import TreeNodeV3
from ..base import BaseBuilderV3
from ..depth_strategy import DepthStrategy
from ..enums import TipoNodo, Profundidad
from .resumen_builder import ResumenBuilderV3
from .contenedor_actividades_builder import ContenedorActividadesBuilderV3


class ProyectoBuilderV3(BaseBuilderV3):
    """
    Builder para el nodo raíz de tipo 'proyecto' (Nivel 0).
    """

    def __init__(self, calculos, repository=None):
        super().__init__(calculos, repository)
        self.resumen_builder = ResumenBuilderV3(calculos, repository)
        self.contenedor_actividades_builder = ContenedorActividadesBuilderV3(calculos, repository)

    def get_tipo_nodo(self) -> str:
        return TipoNodo.PROYECTO.value

    def get_ids_by_parent(self, parent_id: int) -> List[int]:
        return []

    def get_parent_id(self, id: int) -> Optional[int]:
        return None

    def build(
        self,
        id: Optional[int] = None,
        nivel: int = 0,
        es_nodo_objetivo: bool = True,
        depth: Union[str, int] = Profundidad.ALL,
        nivel_nodo_objetivo: int = 0,
    ) -> TreeNodeV3:
        if id is None:
            raise ValueError("Se requiere un ID para construir el proyecto")

        # 1. Obtener datos estandarizados desde el repositorio
        proyecto_data = self.repository.obtener_proyecto(id) if self.repository else None

        if not proyecto_data:
            raise ValueError(f"Proyecto con ID {id} no encontrado")

        hijos = []
        nivel_hijos = nivel + 1  # Resumen y Contenedor de Actividades

        # 2. Evaluar expansión hacia Nivel 1 mediante DepthStrategy
        if DepthStrategy.can_expand(nivel_nodo_objetivo, nivel_hijos, depth):
            # A. Nodo Resumen
            try:
                resumen_nodo = self.resumen_builder.build(
                    proyecto_id=id,
                    nivel=nivel_hijos,
                    es_nodo_objetivo=False,
                    depth=depth,
                    nivel_nodo_objetivo=nivel_nodo_objetivo,
                )
                if resumen_nodo:
                    hijos.append(resumen_nodo)
            except Exception:
                pass

            # B. Contenedor de Actividades
            try:
                contenedor_actividades_nodo = self.contenedor_actividades_builder.build(
                    proyecto_id=id,
                    nivel=nivel_hijos,
                    es_nodo_objetivo=False,
                    depth=depth,
                    nivel_nodo_objetivo=nivel_nodo_objetivo,
                )
                if contenedor_actividades_nodo:
                    hijos.append(contenedor_actividades_nodo)
            except Exception:
                pass

        # 3. Métricas financieras (Nivel principal, fuera del if de expansión)
        planificacion_total = proyecto_data.get('presupuesto', 0.0)
        ejecucion_total = 0.0

        for hijo in hijos:
            if hijo.tipo_nodo == TipoNodo.CONTENEDOR_ACTIVIDADES.value:
                ejecucion_total = hijo.datos.get('ejecucion', {}).get('total', 0.0)

        porcentaje = self._calcular_porcentaje(ejecucion_total, planificacion_total)

        # 4. Estructurar datos
        datos = {
            'codigo': proyecto_data.get('codigo'),
            'nombre': proyecto_data.get('nombre'),
            'descripcion': proyecto_data.get('descripcion'),
            'estado': proyecto_data.get('estado'),
            'estado_display': proyecto_data.get('estado_display'),
            'fecha_inicio': proyecto_data.get('fecha_inicio'),
            'fecha_finalizacion': proyecto_data.get('fecha_finalizacion'),
            'moneda': proyecto_data.get('moneda', 'BOB'),
            'planificacion': {
                'total': planificacion_total,
                'tiene_desglose': len(proyecto_data.get('desglose_financiadores', [])) > 0,
                'desglose_financiadores': proyecto_data.get('desglose_financiadores', []),
            },
            'ejecucion': {
                'total': ejecucion_total,
                'porcentaje': porcentaje,
            },
        }

        # 5. Retorno garantizado
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