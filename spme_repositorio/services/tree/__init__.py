# spme/spme_repositorio/service/tree/__init__.py
from .orchestrator import TreeOrchestrator
from .registry import NodeRegistry
from .enums import NodeType, Direction, DepthType
from .dto import TreeNode, TreeMetadata, TreeResponse, BuildContext
from .builders.proyecto_builder import ProyectoBuilder
from .builders.objetivo_general_builder import ObjetivoGeneralBuilder
from .builders.objetivo_especifico_og_builder import ObjetivoEspecificoOGBuilder
from .builders.indicador_og_builder import IndicadorOGBuilder
from .builders.resultado_og_builder import ResultadoOGBuilder

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
    registry.register_builder(NodeType.PROYECTO.value, ProyectoBuilder())
    registry.register_builder(NodeType.OBJETIVO_GENERAL.value, ObjetivoGeneralBuilder())
    registry.register_builder(NodeType.OBJETIVO_ESPECIFICO_OG.value, ObjetivoEspecificoOGBuilder())
    registry.register_builder(NodeType.INDICADOR_OG.value, IndicadorOGBuilder())      
    registry.register_builder(NodeType.RESULTADO_OG.value, ResultadoOGBuilder())      
    
    # Crear orchestrator
    orchestrator = TreeOrchestrator(registry)
    
    return orchestrator


# Instancia singleton para uso en toda la aplicación
tree_orchestrator = create_tree_orchestrator()