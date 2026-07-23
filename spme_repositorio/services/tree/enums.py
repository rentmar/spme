# NodeType, Direction, DepthType
#Tipo de nodo, direccion y profundidad
from enum import Enum


class NodeType(str, Enum):
    """
    Tipos de nodos disponibles en el Arbol
    """
    PROYECTO = 'proyecto'
    OBJETIVO_GENERAL = 'objetivogeneral'
    OBJETIVO_ESPECIFICO_OG = 'objetivoespecificoog'
    INDICADOR_OG = 'indicadorog'        
    RESULTADO_OG = 'resultadoog'  
    INDICADOR_ROG = 'indicadorrog'        
    PROCESO_ROG = 'procesorog'
    KPI = 'kpi'   
    INDICADOR_OE = 'indicadoroe'          
    RESULTADO_OE = 'resultadooe'          
    PRODUCTO_OE = 'productooe'            
    PROCESO_OE = 'procesooe'              
    PROCESO_POE = 'procesopoe'  
    INDICADOR_ROE = 'indicadorroe'        
    PRODUCTO_ROE = 'productoroe'          
    PROCESO_ROE = 'procesoroe'   
    ACTIVIDAD = 'actividad'            
    TAREA = 'tarea'    
    # Solicitudes/Rendiciones - Actividad
    SOL_FONDOS_ACT = 'solfondosact'
    SOL_VIAJE_ACT = 'solviajeact'
    SOL_PAGO_DIRECTO_ACT = 'solpagodirectoact'
    SOL_REPOSICION_ACT = 'solreposicionact'
    RENDICION_CUENTAS_ACT = 'rendicioncuentasact'
    # Solicitudes/Rendiciones - Tarea
    SOL_FONDOS_SUB = 'solfondossub'
    SOL_VIAJE_SUB = 'solviajesub'
    SOL_PAGO_DIRECTO_SUB = 'solpagodirectosub'
    SOL_REPOSICION_SUB = 'solreposicionsub'
    RENDICION_CUENTAS_SUB = 'rendicioncuentassub'   
    #INFORMES
    INFORME_ACTIVIDAD = 'informeactividad'        
    INFORME_SUBACTIVIDAD = 'informesubactividad'  
            


class Direction(str, Enum):
    """
    Direccion de navegacion en el arbol
    """
    DOWN = 'down'    # Solo descendientes
    UP = 'up'        # Solo ancestros
    BOTH = 'both'    # Ambas direcciones

class DepthType(str, Enum):
    """
    Tipos de profundidad
    """
    SELF = 'self'    # Solo el nodo actual
    ALL = 'all'      # Expansión completa


