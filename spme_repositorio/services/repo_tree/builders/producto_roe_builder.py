# spme/spme_repositorio/services/repo_tree/builders/producto_roe_builder.py
from typing import List, Optional, Any
from spme_estructuracion_proyecto.models import ProductoResultadoOE

from ..enums import RepoNodeType
from ..dto import RepoTreeNode
from ..base import BaseRepoNodeBuilder


class ProductoROERepoBuilder(BaseRepoNodeBuilder):
    """Builder para el nodo Producto ROE."""

    node_type = RepoNodeType.PRODUCTO_ROE.value

    def get_node_type(self) -> str:
        return self.node_type

    def get_ids_by_parent(self, parent_id: int, parent_type: str) -> List[int]:
        if parent_type != RepoNodeType.RESULTADO_OE.value:
            return []

        return list(
            ProductoResultadoOE.objects.filter(
                resultado_oe_id=parent_id
            ).values_list('id', flat=True)
        )

    def get_parent_id(self, child_id: int, parent_type: str) -> Optional[int]:
        try:
            obj = ProductoResultadoOE.objects.get(id=child_id)
            return obj.resultado_oe_id
        except ProductoResultadoOE.DoesNotExist:
            return None

    def build(self, node_id: int, **kwargs) -> RepoTreeNode:
        obj = ProductoResultadoOE.objects.get(id=node_id)

        titulo = obj.descripcion or obj.codigo or f"Producto ROE {obj.id}"

        nodo = RepoTreeNode(
            id=f"{self.node_type}-{obj.id}",
            title=titulo,
            nodo_tipo=self.node_type,
            nodo_id=obj.id,
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