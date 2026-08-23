from typing import List, Optional, Any
from spme_estructuracion_proyecto.models import IndicadorResultadoObjEspecifico

from ..enums import RepoNodeType
from ..dto import RepoTreeNode
from ..base import BaseRepoNodeBuilder


class IndicadorROERepoBuilder(BaseRepoNodeBuilder):
    """Builder para el nodo Indicador ROE."""

    node_type = RepoNodeType.INDICADOR_ROE.value

    def get_node_type(self) -> str:
        return self.node_type

    def get_ids_by_parent(self, parent_id: int, parent_type: str) -> List[int]:
        if parent_type != RepoNodeType.RESULTADO_OE.value:
            return []

        return list(
            IndicadorResultadoObjEspecifico.objects.filter(
                resultado_obj_especifico_id=parent_id
            ).values_list('id', flat=True)
        )

    def get_parent_id(self, child_id: int, parent_type: str) -> Optional[int]:
        try:
            obj = IndicadorResultadoObjEspecifico.objects.get(id=child_id)
            return obj.resultado_obj_especifico_id
        except IndicadorResultadoObjEspecifico.DoesNotExist:
            return None

    def build(self, node_id: int, **kwargs) -> RepoTreeNode:
        obj = IndicadorResultadoObjEspecifico.objects.get(id=node_id)

        nodo = RepoTreeNode(
            id=f"{self.node_type}-{obj.id}",
            title=obj.descripcion or f"Indicador ROE {obj.id}",
            nodo_tipo=self.node_type,
            nodo_id=obj.id,
            codigo=obj.codigo,
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