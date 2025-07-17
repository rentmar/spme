from dependency_injector import containers, providers
from ..presenter.solicitudFondosPresenter import SolicitudFondosPresenter

class SolicitudFondosPresenterContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    solicitudFondosPresenter = providers.Factory(SolicitudFondosPresenter)

