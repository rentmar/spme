# spme/spme_validaciones/services/consolidacion/motor.py
from .modelos import ContextoConsolidacion
from .resolver_estrategia import ResolverEstrategia

class MotorConsolidacion:
    
    def __init__(self):
        self.resolver_estrategia = ResolverEstrategia()

    def consolidar(
        self,
        contexto: ContextoConsolidacion,
    ) -> str:

        estrategia = self.resolver_estrategia.resolver(
            contexto.metodo_resolucion
        )

        return estrategia.consolidar(contexto)
