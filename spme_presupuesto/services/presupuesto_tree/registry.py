# spme/spme_presupuesto/services/presupuesto_tree/registry.py
from typing import Dict, List, Optional, Type
from spme_presupuesto.services.presupuesto_tree.enums import NodeType

class PresupuestoRegistry:
    """
    Registro central de relaciones padre-hijo para el árbol presupuestario.
    """

    def __init__(self):
        self._builders: Dict[str, any] = {}
        self._hierarchy: Dict[str, dict] = {}
        self._initialize_structure()

    def _initialize_structure(self):
        """Define la estructura jerárquica del árbol presupuestario."""
        self._hierarchy = {
            NodeType.PROYECTO.value: {
                'children': [
                    NodeType.ACTIVIDAD.value,
                    NodeType.RESULTADO_ACTIVIDADES.value,
                    NodeType.RESULTADO_TAREAS.value
                ],
                'parent': None,
                'label': 'Proyecto',
                'model': 'Proyecto'
            },
            NodeType.ACTIVIDAD.value: {
                'children': [NodeType.TAREA.value],
                'parent': NodeType.PROYECTO.value,
                'label': 'Actividad',
                'model': 'Actividad'
            },
            NodeType.TAREA.value: {
                'children': [],
                'parent': NodeType.ACTIVIDAD.value,
                'label': 'Tarea',
                'model': 'TareaActividad'
            },
            NodeType.RESULTADO_ACTIVIDADES.value: {
                'children': [],
                'parent': NodeType.PROYECTO.value,
                'label': 'Resultado de Actividades',
                'model': None  # Nodo virtual
            },
            NodeType.RESULTADO_TAREAS.value: {
                'children': [],
                'parent': NodeType.PROYECTO.value,
                'label': 'Resultado de Tareas',
                'model': None  # Nodo virtual
            }
        }

    def register_builder(self, node_type: str, builder):
        """Registra un builder para un tipo de nodo."""
        self._builders[node_type] = builder

    def get_builder(self, node_type: str):
        """Obtiene el builder registrado para un tipo de nodo."""
        if node_type not in self._builders:
            raise ValueError(f"No hay builder registrado para el tipo '{node_type}'")
        return self._builders[node_type]

    def get_children_types(self, node_type: str) -> List[str]:
        """Retorna los tipos de nodo hijo para un tipo dado."""
        node_info = self._hierarchy.get(node_type, {})
        return node_info.get('children', [])

    def get_parent_type(self, node_type: str) -> Optional[str]:
        """Retorna el tipo de nodo padre para un tipo dado."""
        node_info = self._hierarchy.get(node_type, {})
        return node_info.get('parent')

    def get_label(self, node_type: str) -> str:
        """Retorna la etiqueta legible para un tipo de nodo."""
        node_info = self._hierarchy.get(node_type, {})
        return node_info.get('label', node_type)

    def get_model_name(self, node_type: str) -> Optional[str]:
        """Retorna el nombre del modelo asociado al tipo de nodo."""
        node_info = self._hierarchy.get(node_type, {})
        return node_info.get('model')

    def is_virtual(self, node_type: str) -> bool:
        """Indica si el tipo de nodo es virtual (sin modelo de BD)."""
        return self.get_model_name(node_type) is None

    def get_registered_types(self) -> List[str]:
        """Retorna todos los tipos de nodo registrados."""
        return list(self._hierarchy.keys())

    def get_estructura_texto(self) -> str:
        """Retorna una representación textual de la estructura."""
        return 'proyecto > actividad > tarea + resultados'