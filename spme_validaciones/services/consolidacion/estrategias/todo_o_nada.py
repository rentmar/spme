# spme/spme_validaciones/services/consolidacion/estrategias/todo_o_nada.py
from ..modelos import (
    EstadoConsolidado,
    ContextoConsolidacion,
)


class EstrategiaTodoONada:
    def consolidar(
        self,
        contexto: ContextoConsolidacion,
    ) -> str:

        votos = contexto.votos

        #No hay validadores asignado
        if not votos:
            return EstadoConsolidado.SIN_VALIDACIONES

        #Regla de RECHAZO
        if any(
            voto.estado == "RECHAZADO"
            for voto in votos
        ):
            return EstadoConsolidado.RECHAZADO

        #Regla de PENDIENTE
        if any(
            voto.estado == "PENDIENTE"
            for voto in votos
        ):
            return EstadoConsolidado.PENDIENTE

        return EstadoConsolidado.APROBADO