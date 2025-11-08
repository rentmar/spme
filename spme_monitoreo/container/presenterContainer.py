from dependency_injector import containers, providers
from spme_monitoreo.presenter.monitoreoPresenter import (
    SolicitudFondosPresenter,
    ActualizarValidacionSolicitudFondosPresenter,
    ActualizarValidacionRendicionCuentasPresenter,
    ActualizarValidacionSolicitudReembolsoPresenter,
    ActualizarValidacionSolicitudViajePresenter,
    ActualizarValidacionSolicitudPagoDirectoPresenter,
    RendicionCuentasPresenter,
    SolicitudReembolsoPresenter,
    SolicitudViajePresenter,
    SolicitudPagoDirectoPresenter,
    DatosFormularioPresenter,
    FormaPagoPresenter)

class ActualizarValidacionSolicitudReembolsoPresenterContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()
    
    # Proveedor de dependencias
    actualizarValidacionSolicitudReembolsoPresenter = providers.Factory(
        ActualizarValidacionSolicitudReembolsoPresenter
    )

class SolicitudFondosPresenterContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    solicitudFondosPresenter = providers.Factory(SolicitudFondosPresenter)

class RendicionCuentasPresenterContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    rendicionCuentasPresenter = providers.Factory(RendicionCuentasPresenter)

class SolicitudReembolsoPresenterContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()
    
    # Proveedor de dependencias
    solicitudReembolsoPresenter = providers.Factory(SolicitudReembolsoPresenter)

class SolicitudViajePresenterContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    solicitudViajePresenter = providers.Factory(SolicitudViajePresenter)

class SolicitudPagoDirectoPresenterContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    solicitudPagoDirectoPresenter = providers.Factory(SolicitudPagoDirectoPresenter)

class DatosFormularioPresenterContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    datosFormularioPresenter = providers.Factory(DatosFormularioPresenter)

class ActualizarValidacionSolicitudFondosPresenterContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()
    
    # Proveedor de dependencias
    actualizarValidacionSolicitudFondosPresenter = providers.Factory(
        ActualizarValidacionSolicitudFondosPresenter
    )

class ActualizarValidacionRendicionCuentasPresenterContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    actualizarValidacionRendicionCuentasPresenter = providers.Factory(
        ActualizarValidacionRendicionCuentasPresenter
    )

class FormaPagoPresenterContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    formaPagoPresenter = providers.Factory(FormaPagoPresenter)

class ActualizarValidacionSolicitudViajePresenterContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()
    
    # Proveedor de dependencias
    actualizarValidacionSolicitudViajePresenter = providers.Factory(
        ActualizarValidacionSolicitudViajePresenter
    )

class ActualizarValidacionSolicitudPagoDirectoPresenterContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()
    
    # Proveedor de dependencias
    actualizarValidacionSolicitudPagoDirectoPresenter = providers.Factory(
        ActualizarValidacionSolicitudPagoDirectoPresenter
    )