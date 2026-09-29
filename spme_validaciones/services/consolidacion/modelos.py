# spme/spme_validaciones/services/consolidacion/modelos.py
from dataclasses import dataclass, field
from typing import Any


class EstadoConsolidado:
    SIN_VALIDACIONES = "SIN_VALIDACIONES"
    PENDIENTE = "PENDIENTE"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"

class MetodoResolucion:
    TODO_O_NADA = "TODO_O_NADA"
    DECISORIO = "DECISORIO"

@dataclass(frozen=True)
class VotoValidacion:
    usuario_id: Any
    estado: str

@dataclass(frozen=True)
class ConfiguracionMetodo:
    metodo: str
    parametros: dict = field(default_factory=dict)

@dataclass(frozen=True)
class ContextoConsolidacion:
    metodo_resolucion: str
    configuracion: ConfiguracionMetodo
    votos: tuple[VotoValidacion, ...]