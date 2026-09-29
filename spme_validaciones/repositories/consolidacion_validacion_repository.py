# spme/spme_validaciones/repositories/consolidacion_validacion_repository.py
from spme_validaciones.repositories.validacion_solicitud_fondos_repository import (
    ValidacionSolicitudFondosRepository,
)
from spme_validaciones.repositories.validacion_solicitud_viaje_repository import (
    ValidacionSolicitudViajeRepository,
)
from spme_validaciones.repositories.validacion_solicitud_pago_directo_repository import (
    ValidacionSolicitudPagoDirectoRepository,
)
from spme_validaciones.repositories.validacion_solicitud_reembolso_repository import (
    ValidacionSolicitudReembolsoRepository,
)

from spme_validaciones.repositories.validacion_rendicion_cuentas_repository import (
    ValidacionRendicionCuentasRepository,
)

class TipoSolicitudNoSoportado(Exception):
    pass


class ConsolidacionValidacionRepository:
    """
    Repositorio de acceso a las validaciones utilizadas
    por el motor de consolidación.

    Su responsabilidad es únicamente localizar las validaciones
    correspondientes a un tipo de documento y su identificador.

    No calcula estados consolidados.
    """

    REPOSITORIOS = {
        "SOLICITUD_FONDOS": ValidacionSolicitudFondosRepository,
        "SOLICITUD_VIAJE": ValidacionSolicitudViajeRepository,
        "SOLICITUD_PAGO_DIRECTO": ValidacionSolicitudPagoDirectoRepository,
        "SOLICITUD_REEMBOLSO": ValidacionSolicitudReembolsoRepository,
        "RENDICION_CUENTAS": ValidacionRendicionCuentasRepository,
    }

    def __init__(self):
        self._repositorios = {
            tipo: repositorio()
            for tipo, repositorio in self.REPOSITORIOS.items()
        }

    def obtener_validaciones(self, tipo_solicitud, solicitud_id):
        repositorio = self._obtener_repositorio(tipo_solicitud)

        return repositorio.obtener_por_solicitud(solicitud_id)

    def _obtener_repositorio(self, tipo_solicitud):
        try:
            return self._repositorios[tipo_solicitud]
        except KeyError:
            raise TipoSolicitudNoSoportado(
                f"Tipo de solicitud no soportado para consolidación: "
                f"{tipo_solicitud}"
            )

