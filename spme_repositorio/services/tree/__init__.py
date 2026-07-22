# spme/spme_repositorio/service/tree/__init__.py
from .orchestrator import TreeOrchestrator
from .registry import NodeRegistry
from .enums import NodeType, Direction, DepthType
from .dto import TreeNode, TreeMetadata, TreeResponse, BuildContext
from .builders.proyecto_builder import ProyectoBuilder
from .builders.objetivo_general_builder import ObjetivoGeneralBuilder


def create_tree_orchestrator() -> TreeOrchestrator:
    """
    Factory function que crea y configura el orchestrator
    con todos los builders registrados.
    
    Returns:
        TreeOrchestrator configurado y listo para usar
    """
    # Crear registry
    registry = NodeRegistry()
    
    # Registrar builders
    registry.register_builder(NodeType.PROYECTO, ProyectoBuilder())
    registry.register_builder(NodeType.OBJETIVO_GENERAL, ObjetivoGeneralBuilder())
    
    # Crear orchestrator
    orchestrator = TreeOrchestrator(registry)
    
    return orchestrator


# Instancia singleton para uso en toda la aplicación
tree_orchestrator = create_tree_orchestrator()