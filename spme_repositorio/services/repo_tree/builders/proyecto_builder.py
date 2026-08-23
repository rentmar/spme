# spme/spme_repositorio/services/repo_tree/builders/proyecto_builder.py
from typing import List, Optional, Any
from spme_estructuracion_proyecto.models import Proyecto

from ..enums import RepoNodeType
from ..dto import RepoTreeNode
from ..base import BaseRepoNodeBuilder


class ProyectoRepoBuilder(BaseRepoNodeBuilder):
    """Builder para el nodo Proyecto."""

    node_type = RepoNodeType.PROYECTO.value

    def get_node_type(self) -> str:
        return self.node_type

    def get_ids_by_parent(self, parent_id: int, parent_type: str) -> List[int]:
        # Proyecto no tiene padre (es raíz)
        return []

    def get_parent_id(self, child_id: int, parent_type: str) -> Optional[int]:
        # Proyecto no tiene padre
        return None

    def build(self, node_id: int, **kwargs) -> RepoTreeNode:
        proyecto = Proyecto.objects.get(id=node_id)

        nodo = RepoTreeNode(
            id=f"{self.node_type}-{proyecto.id}",
            title=proyecto.titulo or f"Proyecto {proyecto.id}",
            nodo_tipo=self.node_type,
            nodo_id=proyecto.id,
            codigo=proyecto.codigo, 
            upload_enabled=self.registry.get_acceso_repositorio(self.node_type),
            acceso_repositorio=self.registry.get_acceso_repositorio(self.node_type),
            children=[],
        )

        return nodo

    def _extract_data(self, obj: Any) -> dict:
        return {
            'id': obj.id,
            'titulo': obj.titulo,
            'codigo': getattr(obj, 'codigo', None),
        }