# spme/spme_repositorio/services/repo_tree/builders/solicitud_fondos_act_builder.py
from typing import List, Optional, Any
from spme_monitoreo.models import SolicitudFondos

from ..enums import RepoNodeType
from ..dto import RepoTreeNode
from ..base import BaseRepoNodeBuilder


class SolicitudFondosActRepoBuilder(BaseRepoNodeBuilder):
    """Builder para el nodo Solicitud de Fondos de Actividad."""

    node_type = RepoNodeType.SOLICITUD_FONDOS_ACT.value

    def get_node_type(self) -> str:
        return self.node_type

    def get_ids_by_parent(self, parent_id: int, parent_type: str) -> List[int]:
        if parent_type != RepoNodeType.ACTIVIDAD.value:
            return []

        return list(
            SolicitudFondos.objects.filter(
                actividad_id=parent_id,
                tarea__isnull=True,
            ).values_list('id', flat=True)
        )

    def get_parent_id(self, child_id: int, parent_type: str) -> Optional[int]:
        try:
            obj = SolicitudFondos.objects.get(id=child_id)
            return obj.actividad_id
        except SolicitudFondos.DoesNotExist:
            return None

    def build(self, node_id: int, **kwargs) -> RepoTreeNode:
        obj = SolicitudFondos.objects.get(id=node_id)

        titulo = obj.numeroFormulario or f"SF-{obj.id:04d}"

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
            'numero_formulario': obj.numeroFormulario,
        }