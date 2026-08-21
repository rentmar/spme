from typing import List, Optional, Any
from spme_estructuracion_proyecto.models import IndicadorResultadoObjGral

from ..enums import RepoNodeType
from ..dto import RepoTreeNode
from ..base import BaseRepoNodeBuilder


class IndicadorROGRepoBuilder(BaseRepoNodeBuilder):
    """Builder para el nodo Indicador ROG."""

    node_type = RepoNodeType.INDICADOR_ROG.value

    def get_node_type(self) -> str:
        return self.node_type

    def get_ids_by_parent(self, parent_id: int, parent_type: str) -> List[int]:
        if parent_type != RepoNodeType.RESULTADO_OG.value:
            return []

        return list(
            IndicadorResultadoObjGral.objects.filter(
                resultado_og_id=parent_id
            ).values_list('id', flat=True)
        )

    def get_parent_id(self, child_id: int, parent_type: str) -> Optional[int]:
        try:
            obj = IndicadorResultadoObjGral.objects.get(id=child_id)
            return obj.resultado_og_id
        except IndicadorResultadoObjGral.DoesNotExist:
            return None

    def build(self, node_id: int, **kwargs) -> RepoTreeNode:
        obj = IndicadorResultadoObjGral.objects.get(id=node_id)

        nodo = RepoTreeNode(
            id=f"{self.node_type}-{obj.id}",
            title=obj.descripcion or f"Indicador ROG {obj.id}",
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
            'codigo': obj.codigo,
            'descripcion': getattr(obj, 'descripcion', None),
        }