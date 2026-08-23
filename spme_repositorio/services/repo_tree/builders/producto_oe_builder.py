# spme/spme_repositorio/services/repo_tree/builders/producto_oe_builder.py
from typing import List, Optional, Any
from spme_estructuracion_proyecto.models import ProductoOE

from ..enums import RepoNodeType
from ..dto import RepoTreeNode
from ..base import BaseRepoNodeBuilder


class ProductoOERepoBuilder(BaseRepoNodeBuilder):
    """Builder para el nodo Producto OE."""

    node_type = RepoNodeType.PRODUCTO_OE.value

    def get_node_type(self) -> str:
        return self.node_type

    def get_ids_by_parent(self, parent_id: int, parent_type: str) -> List[int]:
        if parent_type != RepoNodeType.OBJETIVO_ESPECIFICO_OG.value:
            return []

        return list(
            ProductoOE.objects.filter(
                objetivo_especifico_id=parent_id
            ).values_list('id', flat=True)
        )

    def get_parent_id(self, child_id: int, parent_type: str) -> Optional[int]:
        try:
            obj = ProductoOE.objects.get(id=child_id)
            return obj.objetivo_especifico_id
        except ProductoOE.DoesNotExist:
            return None

    def build(self, node_id: int, **kwargs) -> RepoTreeNode:
        obj = ProductoOE.objects.get(id=node_id)

        titulo = obj.descripcion or obj.codigo or f"Producto OE {obj.id}"

        nodo = RepoTreeNode(
            id=f"{self.node_type}-{obj.id}",
            title=titulo,
            nodo_tipo=self.node_type,
            nodo_id=obj.id,
            codigo=obj.codigo,
            upload_enabled=self.registry.get_acceso_repositorio(self.node_type),
            acceso_repositorio=self.registry.get_acceso_repositorio(self.node_type),
            children=[],
        )

        if nodo.acceso_repositorio:
            nodo.children = self._build_repository_children(obj, nodo.id)

        return nodo

    def _extract_data(self, obj: Any) -> dict:
        return {
            'id': obj.id,
            'codigo': obj.codigo,
            'descripcion': obj.descripcion,
        }