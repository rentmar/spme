# spme/spme_repositorio/services/repo_tree/builders/actividad_builder.py
from typing import List, Optional, Any
from spme_actividades.models import Actividad

from ..enums import RepoNodeType
from ..dto import RepoTreeNode
from ..base import BaseRepoNodeBuilder


class ActividadRepoBuilder(BaseRepoNodeBuilder):
    """Builder para el nodo Actividad."""

    node_type = RepoNodeType.ACTIVIDAD.value

    def get_node_type(self) -> str:
        return self.node_type

    def get_ids_by_parent(self, parent_id: int, parent_type: str) -> List[int]:
        if parent_type != RepoNodeType.PROYECTO.value:
            return []

        return list(
            Actividad.objects.filter(
                proyecto_id=parent_id,
                estaInactiva=False,
            ).values_list('id', flat=True)
        )

    def get_parent_id(self, child_id: int, parent_type: str) -> Optional[int]:
        try:
            obj = Actividad.objects.get(id=child_id)
            return obj.proyecto_id
        except Actividad.DoesNotExist:
            return None

    def build(self, node_id: int, **kwargs) -> RepoTreeNode:
        obj = Actividad.objects.get(id=node_id)

        # Título: nombreCorto si existe, sino codigo, sino fallback
        titulo = obj.nombreCorto or obj.codigo or f"Actividad {obj.id}"

        nodo = RepoTreeNode(
            id=f"{self.node_type}-{obj.id}",
            title=titulo,
            nodo_tipo=self.node_type,
            nodo_id=obj.id,
            upload_enabled=self.registry.get_acceso_repositorio(self.node_type),
            acceso_repositorio=self.registry.get_acceso_repositorio(self.node_type),
            children=[],
        )

        # Carpetas del repositorio propio
        nodo.children = self._build_repository_children(obj, nodo.id)

        return nodo

    def _extract_data(self, obj: Any) -> dict:
        return {
            'id': obj.id,
            'codigo': obj.codigo,
            'nombre_corto': obj.nombreCorto,
            'estado': obj.estado,
        }