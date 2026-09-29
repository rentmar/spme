# spme/spme_validaciones/services/consolidacion/estrategias/decisorio.py
from ..modelos import EstadoConsolidado, ContextoConsolidacion


class ErrorConfiguracionConsolidacion(Exception):
    pass


class EstrategiaDecisorio:
    PARAMETRO_USUARIO_DECISORIO = "usuarioDecisorio"

    def consolidar(self, contexto: ContextoConsolidacion):
        votos = contexto.votos

        if not votos:
            return EstadoConsolidado.SIN_VALIDACIONES

        if any(voto.estado == "RECHAZADO" for voto in votos):
            return EstadoConsolidado.RECHAZADO

        usuario_decisorio = contexto.configuracion.parametros.get(
            self.PARAMETRO_USUARIO_DECISORIO
        )

        if not usuario_decisorio:
            raise ErrorConfiguracionConsolidacion(
                "DECISORIO requiere el parámetro 'usuarioDecisorio'."
            )

        voto_decisorio = next(
            (
                voto
                for voto in votos
                if voto.usuario_id == usuario_decisorio
            ),
            None,
        )

        if voto_decisorio is None:
            raise ErrorConfiguracionConsolidacion(
                "El usuario decisorio configurado no forma parte "
                "de los validadores del documento."
            )

        if voto_decisorio.estado == "PENDIENTE":
            return EstadoConsolidado.PENDIENTE

        if voto_decisorio.estado == "APROBADO":
            return EstadoConsolidado.APROBADO

        raise ErrorConfiguracionConsolidacion(
            f"El voto del usuario decisorio tiene un estado "
            f"no reconocido: {voto_decisorio.estado}"
        )