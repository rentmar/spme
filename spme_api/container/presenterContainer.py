from dependency_injector import containers, providers
from ..presenters.libroPresenter import LibroPresenter

class PresenterContainer(containers.DeclarativeContainer):
    #Config del contenedor
    config = providers.Configuration()
   

    #Proveeddor de dependencias
    libroPresenter = providers.Factory(LibroPresenter)