from dependency_injector import containers, providers
from ..dataaccess.solicitudFondosDataAccess import SolicitudFondosDataAccess
from ..dataaccess.rendicionCuentasDataAccess import RendicionCuentasDataAccess
from ..dataaccess.solicitudReembolsoDataAccess import SolicitudReembolsoDataAccess
from ..dataaccess.solicitudViajeDataAccess import SolicitudViajeDataAccess
from ..dataaccess.solicitudPagoDirectoDataAccess import SolicitudPagoDirectoDataAccess

class SolicitudFondosDataAccessContainer(containers.DeclarativeContainer):
    """
    Contenedor de acceso a datos de la Solicitud Fondos.
    Proporciona una instancia de SolicitudFondosDataAccess.
    """
    # Configuración del contenedor
    config = providers.Configuration()

    # Proveedor de acceso a datos del SolicitudFondos
    solicitudFondosDataAccess = providers.Singleton(SolicitudFondosDataAccess)

class RendicionCuentasDataAccessContainer(containers.DeclarativeContainer):
    """
    Contenedor de acceso a datos de la Rendicion Cuentas.
    Proporciona una instancia de RendicionCuentasDataAccess.
    """
    # Configuración del contenedor
    config = providers.Configuration()

    rendicionCuentasDataAccess = providers.Singleton(RendicionCuentasDataAccess)

class SolicitudReembolsoDataAccessContainer(containers.DeclarativeContainer):
    """
    Contenedor de acceso a datos de la Solicitud de Reembolso.
    Proporciona una instancia de SolicitudReembolsoDataAccess.
    """
    # Configuración del contenedor
    config = providers.Configuration()


    solicitudReembolsoDataAccess = providers.Singleton(SolicitudReembolsoDataAccess)

class SolicitudViajeDataAccessContainer(containers.DeclarativeContainer):
    """
    Contenedor de acceso a datos de la Solicitud de Viaje.
    Proporciona una instancia de SolicitudViajeDataAccess.
    """
    # Configuración del contenedor
    config = providers.Configuration()

    # Proveedor de acceso a datos de la Solicitud de Viaje
    solicitudViajeDataAccess = providers.Singleton(SolicitudViajeDataAccess)

class SolicitudPagoDirectoDataAccessContainer(containers.DeclarativeContainer):
    """
    Contenedor de acceso a datos de la Solicitud de Pago Directo.
    Proporciona una instancia de SolicitudPagoDirectoDataAccess.
    """
    # Configuración del contenedor
    config = providers.Configuration()

    # Proveedor de acceso a datos de la Solicitud de Pago Directo
    solicitudPagoDirectoDataAccess = providers.Singleton(SolicitudPagoDirectoDataAccess)
