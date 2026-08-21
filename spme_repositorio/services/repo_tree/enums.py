# spme/spme_repositorio/services/repo_tree/enums.py
from enum import Enum


class RepoNodeType(str, Enum):
    """Tipos de nodo del árbol de repositorio."""

    # Estructura
    PROYECTO = 'proyecto'
    OBJETIVO_GENERAL = 'objetivogeneral'
    OBJETIVO_ESPECIFICO_OG = 'objetivoespecificoog'
    INDICADOR_OG = 'indicadorog'
    RESULTADO_OG = 'resultadoog'
    INDICADOR_ROG = 'indicadorrog'
    INDICADOR_OE = 'indicadoroe'
    RESULTADO_OE = 'resultadooe'
    INDICADOR_ROE = 'indicadorroe'
    PRODUCTO_OE = 'productooe'                    
    PRODUCTO_ROE = 'productoroe'                  

    # Actividad y jerarquía
    ACTIVIDAD = 'actividad'
    TAREA = 'tarea'
    SOLICITUD_FONDOS_ACT = 'solicitudfondosact'
    SOLICITUD_FONDOS_TAREA = 'solicitudfondostarea'
    SOLICITUD_REEMBOLSO_ACT = 'solicitudreembolsoact'
    SOLICITUD_REEMBOLSO_TAREA = 'solicitudreembolsotarea'
    SOLICITUD_VIAJE_ACT = 'solicitudviajeact'
    SOLICITUD_VIAJE_TAREA = 'solicitudviajetarea'
    SOLICITUD_PAGO_DIRECTO_ACT = 'solicitudpagodirectoact'
    SOLICITUD_PAGO_DIRECTO_TAREA = 'solicitudpagodirectotarea'
    RENDICION_CUENTAS_ACT = 'rendicioncuentasact'
    RENDICION_CUENTAS_TAREA = 'rendicioncuentastarea'
    INFORME_ACTIVIDAD = 'informeactividad'
    INFORME_TAREA = 'informetarea'

    # Nodos estructurales del repositorio
    CONTENEDOR = 'contenedor'
    CARPETA = 'carpeta'
    ARCHIVO = 'archivo'
    REFERENCIA = 'referencia'