from dependency_injector import containers, providers
from spme_monitoreo.dataaccess.solicitudFondosDataAccess import SolicitudFondosDataAccess
from spme_monitoreo.dataaccess.rendicionCuentasDataAccess import RendicionCuentasDataAccess
from spme_monitoreo.dataaccess.solicitudReembolsoDataAccess import SolicitudReembolsoDataAccess
from spme_monitoreo.dataaccess.solicitudViajeDataAccess import SolicitudViajeDataAccess
from spme_monitoreo.dataaccess.solicitudPagoDirectoDataAccess import SolicitudPagoDirectoDataAccess
from spme_monitoreo.dataaccess.formaPagoDataAccess import FormaPagoDataAccess
from spme_monitoreo.dataaccess.solicitudViajeDataAccess import SolicitudViajeDataAccess

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

class FormaPagoDataAccessContainer(containers.DeclarativeContainer):
    """
    Contenedor de acceso a datos de la Forma de pago.
    Proporciona una instancia de FormaPagoDataAccess.
    """
    # Configuración del contenedor
    config = providers.Configuration()

    # Proveedor de acceso a datos de la Solicitud de Pago Directo
    formaPagoDataAccess = providers.Singleton(FormaPagoDataAccess)

class FormaPagoDataAccessContainer(containers.DeclarativeContainer):
    """
    Contenedor de acceso a datos de la Forma de pago.
    Proporciona una instancia de FormaPagoDataAccess.
    """
    # Configuración del contenedor
    config = providers.Configuration()

    # Proveedor de acceso a datos de la Forma de Pago
    formaPagoDataAccess = providers.Singleton(FormaPagoDataAccess)

class SolicitudViajeDataAccessContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()
    
    # Proveedor de dependencias
    solicitudViajeDataAccess = providers.Singleton(SolicitudViajeDataAccess)
