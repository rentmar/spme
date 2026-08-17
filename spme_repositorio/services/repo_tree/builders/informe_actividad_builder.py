# spme/spme_repositorio/services/repo_tree/builders/informe_actividad_builder.py
from typing import List, Optional, Any
from spme_monitoreo.models import InformeActividadPrincipal

from ..enums import RepoNodeType
from ..dto import RepoTreeNode
from ..base import BaseRepoNodeBuilder


class InformeActividadRepoBuilder(BaseRepoNodeBuilder):
    """Builder para el nodo Informe de Actividad."""

    node_type = RepoNodeType.INFORME_ACTIVIDAD.value

    def get_node_type(self) -> str:
        return self.node_type

    def get_ids_by_parent(self, parent_id: int, parent_type: str) -> List[int]:
        if parent_type != RepoNodeType.ACTIVIDAD.value:
            return []

        return list(
            InformeActividadPrincipal.objects.filter(
                actividad_id=parent_id,
            ).values_list('id', flat=True)
        )

    def get_parent_id(self, child_id: int, parent_type: str) -> Optional[int]:
        try:
            obj = InformeActividadPrincipal.objects.get(id=child_id)
            return obj.actividad_id
        except InformeActividadPrincipal.DoesNotExist:
            return None

    def build(self, node_id: int, **kwargs) -> RepoTreeNode:
        obj = InformeActividadPrincipal.objects.get(id=node_id)

        titulo = obj.numeroInforme or f"INF-{obj.id:04d}"

        nodo = RepoTreeNode(
            id=f"{self.node_type}-{obj.id}",
            title=titulo,
            nodo_tipo=self.node_type,
            nodo_id=obj.id,
            upload_enabled=True,
            children=[],
        )

        nodo.children = self._build_repository_children(obj, nodo.id)

        return nodo

    def _extract_data(self, obj: Any) -> dict:
        return {
            'id': obj.id,
            'numero_informe': obj.numeroInforme,
        }