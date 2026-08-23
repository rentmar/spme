# spme/spme_repositorio/services/repo_tree/builders/informe_tarea_builder.py
from typing import List, Optional, Any
from spme_monitoreo.models import InformeTareaPrincipal

from ..enums import RepoNodeType
from ..dto import RepoTreeNode
from ..base import BaseRepoNodeBuilder


class InformeTareaRepoBuilder(BaseRepoNodeBuilder):
    """Builder para el nodo Informe de Tarea."""

    node_type = RepoNodeType.INFORME_TAREA.value

    def get_node_type(self) -> str:
        return self.node_type

    def get_ids_by_parent(self, parent_id: int, parent_type: str) -> List[int]:
        if parent_type != RepoNodeType.TAREA.value:
            return []

        return list(
            InformeTareaPrincipal.objects.filter(
                tarea_id=parent_id,
            ).values_list('id', flat=True)
        )

    def get_parent_id(self, child_id: int, parent_type: str) -> Optional[int]:
        try:
            obj = InformeTareaPrincipal.objects.get(id=child_id)
            return obj.tarea_id
        except InformeTareaPrincipal.DoesNotExist:
            return None

    def build(self, node_id: int, **kwargs) -> RepoTreeNode:
        obj = InformeTareaPrincipal.objects.get(id=node_id)

        titulo = obj.numeroInforme or f"INF-{obj.id:04d}"

        nodo = RepoTreeNode(
            id=f"{self.node_type}-{obj.id}",
            title=titulo,
            nodo_tipo=self.node_type,
            nodo_id=obj.id,
            codigo=obj.numeroFormulario,
            upload_enabled=self.registry.get_acceso_repositorio(self.node_type),
            acceso_repositorio=self.registry.get_acceso_repositorio(self.node_type),
            children=[],
        )

        nodo.children = self._build_repository_children(obj, nodo.id)

        return nodo

    def _extract_data(self, obj: Any) -> dict:
        return {
            'id': obj.id,
            'numero_informe': obj.numeroInforme,
        }