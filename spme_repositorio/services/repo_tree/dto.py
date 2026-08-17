# spme/spme_repositorio/services/repo_tree/dto.py
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class RepoTreeNode:
    """
    Nodo del árbol de repositorio.
    """

    id: str
    title: str
    nodo_tipo: str
    nodo_id: Optional[int] = None
    upload_enabled: Optional[bool] = None
    tipo_archivo: Optional[str] = None
    archivo_id: Optional[int] = None
    adjunto_id: Optional[int] = None
    descargar_enabled: Optional[bool] = None
    borrar_enabled: Optional[bool] = None
    categoria: Optional[str] = None
    url: Optional[str] = None
    referencia_id: Optional[int] = None
    children: List['RepoTreeNode'] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el nodo a diccionario para JSON.
        """
        result = {
            'id': self.id,
            'title': self.title,
            'nodo_tipo': self.nodo_tipo,
        }

        if self.nodo_id is not None:
            result['nodo_id'] = self.nodo_id

        if self.upload_enabled is not None:
            result['upload_enabled'] = self.upload_enabled

        if self.tipo_archivo is not None:
            result['tipo_archivo'] = self.tipo_archivo

        if self.archivo_id is not None:
            result['archivo_id'] = self.archivo_id

        if self.adjunto_id is not None:
            result['adjunto_id'] = self.adjunto_id

        if self.descargar_enabled is not None:
            result['descargar_enabled'] = self.descargar_enabled

        if self.borrar_enabled is not None:
            result['borrar_enabled'] = self.borrar_enabled

        if self.categoria is not None:
            result['categoria'] = self.categoria

        if self.url is not None:
            result['url'] = self.url

        if self.referencia_id is not None:
            result['referencia_id'] = self.referencia_id

        if self.children:
            result['children'] = [child.to_dict() for child in self.children]
        else:
            result['children'] = []

        return result


@dataclass
class RepoTreeResponse:
    """
    Respuesta completa del árbol de repositorio.
    """
    proyecto_id: int
    proyecto_nombre: str
    tree: List[RepoTreeNode]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'proyecto_id': self.proyecto_id,
            'proyecto_nombre': self.proyecto_nombre,
            'tree': [node.to_dict() for node in self.tree],
        }