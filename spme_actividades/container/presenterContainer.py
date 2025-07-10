from dependency_injector import containers, providers
from ..presenters.actividadesPresenter import ActividadesPresenter

class ActividadesPresenterContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    actividadesPresenter = providers.Factory(ActividadesPresenter)