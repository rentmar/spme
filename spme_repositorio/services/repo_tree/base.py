# spme/spme_repositorio/services/repo_tree/base.py
from abc import ABC, abstractmethod
from typing import List, Optional, Any
from django.contrib.contenttypes.models import ContentType

from .enums import RepoNodeType
from .dto import RepoTreeNode
from .registry import RepoNodeRegistry


class BaseRepoNodeBuilder(ABC):
    """Builder base para nodos del árbol de repositorio."""

    node_type: str = ''

    TIPO_ARCHIVO_LABELS = {
        'DOCUMENTO': 'Documentos',
        'IMAGEN': 'Imágenes',
        'VIDEO': 'Videos',
        'AUDIO': 'Audio',
        'OTRO': 'Otros',
        'REFERENCIAS': 'Referencias',
    }

    TIPO_ARCHIVO_ORDEN = [
        'DOCUMENTO',
        'IMAGEN',
        'VIDEO',
        'AUDIO',
        'OTRO',
        'REFERENCIAS',
    ]

    def __init__(self, registry: RepoNodeRegistry):
        self.registry = registry

    @abstractmethod
    def get_node_type(self) -> str:
        pass

    @abstractmethod
    def get_ids_by_parent(self, parent_id: int, parent_type: str) -> List[int]:
        pass

    @abstractmethod
    def get_parent_id(self, child_id: int, parent_type: str) -> Optional[int]:
        pass

    @abstractmethod
    def build(self, node_id: int, **kwargs) -> RepoTreeNode:
        pass

    @abstractmethod
    def _extract_data(self, obj: Any) -> dict:
        pass

    def get_model(self):
        return self.registry.get_model(self.node_type)

    def get_fk_field(self) -> Optional[str]:
        return self.registry.get_fk_field(self.node_type)

    def get_filter_extra(self) -> Optional[dict]:
        return self.registry.get_filter_extra(self.node_type)

    def get_children_types(self) -> List[str]:
        return self.registry.get_children_types(self.node_type)

    def get_parent_type(self) -> Optional[str]:
        return self.registry.get_parent_type(self.node_type)

    # ================================================================
    # MÉTODOS DE REPOSITORIO
    # ================================================================

    def _build_repository_children(self, obj: Any, nodo_padre_id: str) -> List[RepoTreeNode]:
        """
        Construye las carpetas por tipo de archivo y referencias
        para un nodo con acceso al repositorio.
        """
        from spme_repositorio.services.storage.adjunto_service import AdjuntoService
        from spme_repositorio.services.referencias.referencia_service import ReferenciaService

        adjunto_service = AdjuntoService()
        referencia_service = ReferenciaService()

        # Obtener adjuntos del objeto
        adjuntos = adjunto_service.obtener_adjuntos(obj)

        # Obtener referencias del objeto
        referencias = referencia_service.obtener_referencias(obj)

        # Agrupar adjuntos por tipo_archivo
        adjuntos_por_tipo = {}
        for adjunto in adjuntos:
            tipo = adjunto.archivo.tipo_archivo if adjunto.archivo else 'OTRO'
            if tipo not in adjuntos_por_tipo:
                adjuntos_por_tipo[tipo] = []
            adjuntos_por_tipo[tipo].append(adjunto)

        children = []

        # Construir carpetas por tipo en orden definido
        for tipo in self.TIPO_ARCHIVO_ORDEN:
            if tipo == 'REFERENCIAS':
                continue

            adjuntos_tipo = adjuntos_por_tipo.get(tipo, [])
            if adjuntos_tipo:
                carpeta = self._build_carpeta_tipo(
                    nodo_padre_id=nodo_padre_id,
                    tipo_archivo=tipo,
                    adjuntos=adjuntos_tipo,
                )
                children.append(carpeta)

        # Construir carpeta de referencias
        if referencias:
            carpeta_refs = self._build_carpeta_referencias(
                nodo_padre_id=nodo_padre_id,
                referencias=referencias,
            )
            children.append(carpeta_refs)

        return children

    def _build_carpeta_tipo(self, nodo_padre_id: str, tipo_archivo: str, adjuntos: List[Any]) -> RepoTreeNode:
        """Construye una carpeta por tipo de archivo."""
        label = self.TIPO_ARCHIVO_LABELS.get(tipo_archivo, tipo_archivo)
        cantidad = len(adjuntos)

        carpeta = RepoTreeNode(
            id=f"{nodo_padre_id}-carpeta-{tipo_archivo}",
            title=f"{label} ({cantidad})",
            nodo_tipo=RepoNodeType.CARPETA.value,
            tipo_archivo=tipo_archivo,
            children=[],
        )

        for adjunto in adjuntos:
            archivo_nodo = self._build_archivo_node(adjunto)
            carpeta.children.append(archivo_nodo)

        return carpeta

    def _build_carpeta_referencias(self, nodo_padre_id: str, referencias: List[Any]) -> RepoTreeNode:
        """Construye la carpeta de referencias externas."""
        cantidad = len(referencias)

        carpeta = RepoTreeNode(
            id=f"{nodo_padre_id}-carpeta-REFERENCIAS",
            title=f"Referencias ({cantidad})",
            nodo_tipo=RepoNodeType.CARPETA.value,
            tipo_archivo='REFERENCIAS',
            children=[],
        )

        for referencia in referencias:
            ref_nodo = self._build_referencia_node(referencia)
            carpeta.children.append(ref_nodo)

        return carpeta

    def _build_archivo_node(self, adjunto: Any) -> RepoTreeNode:
        """Construye un nodo de archivo individual."""
        archivo = adjunto.archivo

        return RepoTreeNode(
            id=f"archivo-{archivo.id}",
            title=archivo.nombre_original,
            nodo_tipo=RepoNodeType.ARCHIVO.value,
            tipo_archivo=archivo.tipo_archivo,
            archivo_id=archivo.id,
            adjunto_id=adjunto.id,
            descargar_enabled=True,
            borrar_enabled=True,
        )

    def _build_referencia_node(self, referencia: Any) -> RepoTreeNode:
        """Construye un nodo de referencia individual."""
        return RepoTreeNode(
            id=f"referencia-{referencia.id}",
            title=referencia.nombre or referencia.url[:100],
            nodo_tipo=RepoNodeType.REFERENCIA.value,
            tipo_archivo='REFERENCIAS',
            categoria=referencia.categoria or 'OTRO',
            url=referencia.url,
            referencia_id=referencia.id,
            borrar_enabled=True,
        )

    # ================================================================
    # MÉTODOS DE CONTENEDORES
    # ================================================================

    def _build_contenedor(self, nodo_padre_id: str, titulo: str, children: List[RepoTreeNode]) -> RepoTreeNode:
        return RepoTreeNode(
            id=f"{nodo_padre_id}-contenedor-{titulo.lower().replace(' ', '_')}",
            title=titulo,
            nodo_tipo=RepoNodeType.CONTENEDOR.value,
            children=children,
        )

    def _build_contenedor_vacio(self, nodo_padre_id: str, titulo: str) -> RepoTreeNode:
        return RepoTreeNode(
            id=f"{nodo_padre_id}-contenedor-{titulo.lower().replace(' ', '_')}",
            title=titulo,
            nodo_tipo=RepoNodeType.CONTENEDOR.value,
            children=[],
        )

    def _build_title(self, obj: Any, prefix: str = '') -> str:
        return str(obj)

    def _sanitize_nombre(self, nombre: str) -> str:
        import re
        return re.sub(r'[^a-zA-Z0-9_-]', '_', nombre.lower())