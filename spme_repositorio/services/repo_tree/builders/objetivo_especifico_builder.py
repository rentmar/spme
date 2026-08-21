# spme/spme_repositorio/services/repo_tree/builders/objetivo_especifico_builder.py
from typing import List, Optional, Any
from spme_estructuracion_proyecto.models import ObjetivoEspecificoProyecto

from ..enums import RepoNodeType
from ..dto import RepoTreeNode
from ..base import BaseRepoNodeBuilder


class ObjetivoEspecificoRepoBuilder(BaseRepoNodeBuilder):
    """Builder para el nodo Objetivo Específico."""

    node_type = RepoNodeType.OBJETIVO_ESPECIFICO_OG.value

    def get_node_type(self) -> str:
        return self.node_type

    def get_ids_by_parent(self, parent_id: int, parent_type: str) -> List[int]:
        if parent_type != RepoNodeType.OBJETIVO_GENERAL.value:
            return []

        return list(
            ObjetivoEspecificoProyecto.objects.filter(
                objetivo_general_id=parent_id
            ).values_list('id', flat=True)
        )

    def get_parent_id(self, child_id: int, parent_type: str) -> Optional[int]:
        try:
            obj = ObjetivoEspecificoProyecto.objects.get(id=child_id)
            return obj.objetivo_general_id
        except ObjetivoEspecificoProyecto.DoesNotExist:
            return None

    def build(self, node_id: int, **kwargs) -> RepoTreeNode:
        obj = ObjetivoEspecificoProyecto.objects.get(id=node_id)

        nodo = RepoTreeNode(
            id=f"{self.node_type}-{obj.id}",
            title=obj.descripcion or f"Objetivo Específico {obj.id}",
            nodo_tipo=self.node_type,
            nodo_id=obj.id,
            upload_enabled=self.registry.get_acceso_repositorio(self.node_type),
            acceso_repositorio=self.registry.get_acceso_repositorio(self.node_type),
            children=[],
        )

        return nodo

    def _extract_data(self, obj: Any) -> dict:
        return {
            'id': obj.id,
            'codigo': obj.codigo,
            'descripcion': getattr(obj, 'descripcion', None),
        }