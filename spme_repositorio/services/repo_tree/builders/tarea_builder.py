# spme/spme_repositorio/services/repo_tree/builders/tarea_builder.py
from typing import List, Optional, Any
from spme_actividades.models import TareaActividad

from ..enums import RepoNodeType
from ..dto import RepoTreeNode
from ..base import BaseRepoNodeBuilder


class TareaRepoBuilder(BaseRepoNodeBuilder):
    """Builder para el nodo Tarea."""

    node_type = RepoNodeType.TAREA.value

    def get_node_type(self) -> str:
        return self.node_type

    def get_ids_by_parent(self, parent_id: int, parent_type: str) -> List[int]:
        if parent_type != RepoNodeType.ACTIVIDAD.value:
            return []

        return list(
            TareaActividad.objects.filter(
                actividad_id=parent_id
            ).values_list('id', flat=True)
        )

    def get_parent_id(self, child_id: int, parent_type: str) -> Optional[int]:
        try:
            obj = TareaActividad.objects.get(id=child_id)
            return obj.actividad_id
        except TareaActividad.DoesNotExist:
            return None

    def build(self, node_id: int, **kwargs) -> RepoTreeNode:
        obj = TareaActividad.objects.get(id=node_id)

        # Título: titulo si existe, sino codigo, sino fallback
        titulo = obj.titulo or obj.codigo or f"Tarea {obj.id}"

        nodo = RepoTreeNode(
            id=f"{self.node_type}-{obj.id}",
            title=titulo,
            nodo_tipo=self.node_type,
            nodo_id=obj.id,
            upload_enabled=True,
            children=[],
        )

        # Carpetas del repositorio propio
        nodo.children = self._build_repository_children(obj, nodo.id)

        return nodo

    def _extract_data(self, obj: Any) -> dict:
        return {
            'id': obj.id,
            'codigo': obj.codigo,
            'titulo': obj.titulo,
            'estado': obj.estado,
        }