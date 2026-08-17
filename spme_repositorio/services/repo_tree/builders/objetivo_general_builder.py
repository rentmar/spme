from typing import List, Optional, Any
from spme_estructuracion_proyecto.models import ObjetivoGeneralProyecto

from ..enums import RepoNodeType
from ..dto import RepoTreeNode
from ..base import BaseRepoNodeBuilder


class ObjetivoGeneralRepoBuilder(BaseRepoNodeBuilder):
    """Builder para el nodo Objetivo General."""

    node_type = RepoNodeType.OBJETIVO_GENERAL.value

    def get_node_type(self) -> str:
        return self.node_type

    def get_ids_by_parent(self, parent_id: int, parent_type: str) -> List[int]:
        if parent_type != RepoNodeType.PROYECTO.value:
            return []

        return list(
            ObjetivoGeneralProyecto.objects.filter(
                proyecto_id=parent_id
            ).values_list('id', flat=True)
        )

    def get_parent_id(self, child_id: int, parent_type: str) -> Optional[int]:
        try:
            obj = ObjetivoGeneralProyecto.objects.get(id=child_id)
            return obj.proyecto_id
        except ObjetivoGeneralProyecto.DoesNotExist:
            return None

    def build(self, node_id: int, **kwargs) -> RepoTreeNode:
        obj = ObjetivoGeneralProyecto.objects.get(id=node_id)

        nodo = RepoTreeNode(
            id=f"{self.node_type}-{obj.id}",
            title=obj.descripcion or f"Objetivo General {obj.id}",
            nodo_tipo=self.node_type,
            nodo_id=obj.id,
            upload_enabled=False,
            children=[],
        )

        return nodo

    def _extract_data(self, obj: Any) -> dict:
        return {
            'id': obj.id,
            'nombre': obj.nombre,
            'descripcion': getattr(obj, 'descripcion', None),
        }