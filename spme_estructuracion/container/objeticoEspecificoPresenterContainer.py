from dependency_injector import containers, providers

from ..presenters.ObjetivoEspecificoPresenter import ObjetivoEspecificoPresenter

class ObjetivoEspecificoPresenterContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    objetivoEspecificoPresenter = providers.Factory(ObjetivoEspecificoPresenter)

    