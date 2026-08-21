# spme/spme_repositorio/services/repo_tree/builders/solicitud_reembolso_tarea_builder.py
from typing import List, Optional, Any
from spme_monitoreo.models import SolicitudReembolso

from ..enums import RepoNodeType
from ..dto import RepoTreeNode
from ..base import BaseRepoNodeBuilder


class SolicitudReembolsoTareaRepoBuilder(BaseRepoNodeBuilder):
    """Builder para el nodo Solicitud de Reembolso de Tarea."""

    node_type = RepoNodeType.SOLICITUD_REEMBOLSO_TAREA.value

    def get_node_type(self) -> str:
        return self.node_type

    def get_ids_by_parent(self, parent_id: int, parent_type: str) -> List[int]:
        if parent_type != RepoNodeType.TAREA.value:
            return []

        return list(
            SolicitudReembolso.objects.filter(
                tarea_id=parent_id,
            ).values_list('id', flat=True)
        )

    def get_parent_id(self, child_id: int, parent_type: str) -> Optional[int]:
        try:
            obj = SolicitudReembolso.objects.get(id=child_id)
            return obj.tarea_id
        except SolicitudReembolso.DoesNotExist:
            return None

    def build(self, node_id: int, **kwargs) -> RepoTreeNode:
        obj = SolicitudReembolso.objects.get(id=node_id)

        titulo = obj.numeroFormulario or f"SR-{obj.id:04d}"

        nodo = RepoTreeNode(
            id=f"{self.node_type}-{obj.id}",
            title=titulo,
            nodo_tipo=self.node_type,
            nodo_id=obj.id,
            upload_enabled=self.registry.get_acceso_repositorio(self.node_type),
            acceso_repositorio=self.registry.get_acceso_repositorio(self.node_type),
            children=[],
        )

        nodo.children = self._build_repository_children(obj, nodo.id)

        return nodo

    def _extract_data(self, obj: Any) -> dict:
        return {
            'id': obj.id,
            'numero_formulario': obj.numeroFormulario,
        }