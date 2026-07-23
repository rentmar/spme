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
from .builders.indicador_rog_builder import IndicadorROGBuilder
from .builders.proceso_rog_builder import ProcesoROGBuilder
from .builders.kpi_builder import KpiBuilder
from .builders.indicador_oe_builder import IndicadorOEBuilder
from .builders.resultado_oe_builder import ResultadoOEBuilder
from .builders.producto_oe_builder import ProductoOEBuilder
from .builders.proceso_oe_builder import ProcesoOEBuilder
from .builders.proceso_poe_builder import ProcesoPOEBuilder
from .builders.indicador_roe_builder import IndicadorROEBuilder
from .builders.producto_roe_builder import ProductoROEBuilder
from .builders.proceso_roe_builder import ProcesoROEBuilder
from .builders.actividad_builder import ActividadBuilder
from .builders.tarea_builder import TareaBuilder
from .builders.solfondosact_builder import SolFondosActBuilder
from .builders.solfondossub_builder import SolFondosSubBuilder
from .builders.solviajeact_builder import SolViajeActBuilder
from .builders.solviajesub_builder import SolViajeSubBuilder
from .builders.solpagodirectoact_builder import SolPagoDirectoActBuilder
from .builders.solpagodirectosub_builder import SolPagoDirectoSubBuilder
from .builders.solreposicionact_builder import SolReposicionActBuilder
from .builders.solreposicionsub_builder import SolReposicionSubBuilder
from .builders.rendicioncuentasact_builder import RendicionCuentasActBuilder
from .builders.rendicioncuentassub_builder import RendicionCuentasSubBuilder


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
    registry.register_builder(NodeType.INDICADOR_ROG.value, IndicadorROGBuilder())  
    registry.register_builder(NodeType.PROCESO_ROG.value, ProcesoROGBuilder())   
    registry.register_builder(NodeType.KPI.value, KpiBuilder())
    registry.register_builder(NodeType.INDICADOR_OE.value, IndicadorOEBuilder())      
    registry.register_builder(NodeType.RESULTADO_OE.value, ResultadoOEBuilder())      
    registry.register_builder(NodeType.PRODUCTO_OE.value, ProductoOEBuilder())        
    registry.register_builder(NodeType.PROCESO_OE.value, ProcesoOEBuilder())          
    registry.register_builder(NodeType.PROCESO_POE.value, ProcesoPOEBuilder())        
    registry.register_builder(NodeType.INDICADOR_ROE.value, IndicadorROEBuilder())    
    registry.register_builder(NodeType.PRODUCTO_ROE.value, ProductoROEBuilder())      
    registry.register_builder(NodeType.PROCESO_ROE.value, ProcesoROEBuilder())      
    registry.register_builder(NodeType.ACTIVIDAD.value, ActividadBuilder())    
    registry.register_builder(NodeType.TAREA.value, TareaBuilder())   
    registry.register_builder(NodeType.SOL_FONDOS_ACT.value, SolFondosActBuilder())
    registry.register_builder(NodeType.SOL_FONDOS_SUB.value, SolFondosSubBuilder())
    registry.register_builder(NodeType.SOL_VIAJE_ACT.value, SolViajeActBuilder())
    registry.register_builder(NodeType.SOL_VIAJE_SUB.value, SolViajeSubBuilder())
    registry.register_builder(NodeType.SOL_PAGO_DIRECTO_ACT.value, SolPagoDirectoActBuilder())
    registry.register_builder(NodeType.SOL_PAGO_DIRECTO_SUB.value, SolPagoDirectoSubBuilder())
    registry.register_builder(NodeType.SOL_REPOSICION_ACT.value, SolReposicionActBuilder())
    registry.register_builder(NodeType.SOL_REPOSICION_SUB.value, SolReposicionSubBuilder())
    registry.register_builder(NodeType.RENDICION_CUENTAS_ACT.value, RendicionCuentasActBuilder())
    registry.register_builder(NodeType.RENDICION_CUENTAS_SUB.value, RendicionCuentasSubBuilder())
             
    
    # Crear orchestrator
    orchestrator = TreeOrchestrator(registry)
    
    return orchestrator


# Instancia singleton para uso en toda la aplicación
tree_orchestrator = create_tree_orchestrator()