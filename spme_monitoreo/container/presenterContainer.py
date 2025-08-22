from dependency_injector import containers, providers
from ..presenter.monitoreoPresenter import SolicitudFondosPresenter, RendicionCuentasPresenter,SolicitudReembolsoPresenter,SolicitudViajePresenter,SolicitudPagoDirectoPresenter,DatosFormularioPresenter

class SolicitudFondosPresenterContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    solicitudFondosPresenter = providers.Factory(SolicitudFondosPresenter)

class RendicionCuentasPresenterContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    rendicionCuentasPresenterPresenter = providers.Factory(RendicionCuentasPresenter)


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
