# spme/spme_tree_reporter/services/renderers/__init__.py
"""
RendererRegistry: Mapea tipo_nodo → renderer.
Punto central de registro. Para agregar un nuevo renderer:
1. Crear archivo en services/renderers/
2. Importar la clase aquí
3. Agregar al diccionario _renderers
"""

# === Renderers de Estructura (16 tipos de nodo) ===
from .proyecto import ProyectoRenderer
from .objetivo_general import ObjetivoGeneralRenderer
from .objetivo_especifico_og import ObjetivoEspecificoOGRenderer
from .indicador_og import IndicadorOGRenderer
from .indicador_oe import IndicadorOERenderer
from .indicador_rog import IndicadorROGRenderer
from .indicador_roe import IndicadorROERenderer
from .resultado_og import ResultadoOGRenderer
from .resultado_oe import ResultadoOERenderer
from .producto_oe import ProductoOERenderer
from .producto_roe import ProductoROERenderer
from .proceso import ProcesoRenderer
from .kpi import KPIRenderer

# === Renderers de Actividades y Jerarquía (14 tipos de nodo) ===
from .actividad import ActividadRenderer
from .tarea import TareaRenderer
from .solicitud_fondos import SolicitudFondosRenderer
from .solicitud_viaje import SolicitudViajeRenderer
from .solicitud_pago_directo import SolicitudPagoDirectoRenderer
from .solicitud_reposicion import SolicitudReposicionRenderer
from .rendicion_cuentas import RendicionCuentasRenderer
from .informe_actividad import InformeActividadRenderer
from .informe_tarea import InformeTareaRenderer


class RendererRegistry:
    """
    Registro central de renderers.
    
    Uso:
        registry = RendererRegistry()
        renderer = registry.get('proyecto')
        renderer.render(nodo, context)
    """
    
    def __init__(self):
        self._renderers = {
            # =============================================================
            # ESTRUCTURA DEL PROYECTO (16)
            # =============================================================
            
            # Nivel 0
            'proyecto': ProyectoRenderer(),
            
            # Nivel 1
            'objetivogeneral': ObjetivoGeneralRenderer(),
            
            # Nivel 2 - Hijos de Objetivo General
            'objetivoespecificoog': ObjetivoEspecificoOGRenderer(),
            'indicadorog': IndicadorOGRenderer(),
            'resultadoog': ResultadoOGRenderer(),
            'kpi': KPIRenderer(),
            
            # Nivel 3 - Hijos de Objetivo Específico
            'indicadoroe': IndicadorOERenderer(),
            'resultadooe': ResultadoOERenderer(),
            'productooe': ProductoOERenderer(),
            'procesooe': ProcesoRenderer(),
            
            # Nivel 3 - Hijos de Resultado OG
            'indicadorrog': IndicadorROGRenderer(),
            'procesorog': ProcesoRenderer(),
            
            # Nivel 4 - Hijos de Resultado OE
            'indicadorroe': IndicadorROERenderer(),
            'productoroe': ProductoROERenderer(),
            'procesoroe': ProcesoRenderer(),
            
            # Nivel 4 - Hijos de Producto OE
            'procesopoe': ProcesoRenderer(),
            
            # =============================================================
            # ACTIVIDADES Y JERARQUÍA (14)
            # =============================================================
            
            # Actividad y Tarea
            'actividad': ActividadRenderer(),
            'tarea': TareaRenderer(),
            
            # Solicitudes y Rendiciones de Actividad (sufijo 'act')
            'solfondosact': SolicitudFondosRenderer(),
            'solviajeact': SolicitudViajeRenderer(),
            'solpagodirectoact': SolicitudPagoDirectoRenderer(),
            'solreposicionact': SolicitudReposicionRenderer(),
            'rendicioncuentasact': RendicionCuentasRenderer(),
            
            # Solicitudes y Rendiciones de Tarea (sufijo 'sub')
            'solfondossub': SolicitudFondosRenderer(),
            'solviajesub': SolicitudViajeRenderer(),
            'solpagodirectosub': SolicitudPagoDirectoRenderer(),
            'solreposicionsub': SolicitudReposicionRenderer(),
            'rendicioncuentassub': RendicionCuentasRenderer(),
            
            # Informes
            'informeactividad': InformeActividadRenderer(),
            'informesubactividad': InformeTareaRenderer(),
        }
    
    def get(self, tipo_nodo: str):
        """
        Retorna el renderer para un tipo de nodo.
        
        Args:
            tipo_nodo: String del tipo de nodo del árbol
        
        Returns:
            BaseRenderer o None si no hay renderer registrado
        """
        return self._renderers.get(tipo_nodo)
    
    def get_registered_types(self) -> list:
        """Retorna la lista de tipos de nodo registrados."""
        return list(self._renderers.keys())
    
    def register(self, tipo_nodo: str, renderer):
        """
        Registra un nuevo renderer en tiempo de ejecución.
        Útil para extender sin modificar este archivo.
        
        Args:
            tipo_nodo: String del tipo de nodo
            renderer: Instancia de BaseRenderer
        """
        self._renderers[tipo_nodo] = renderer