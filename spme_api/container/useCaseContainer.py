from dependency_injector import containers, providers
from ..domain.usecases.getLibroUseCase import GetLibroUseCase


class UseCaseContainer(containers.DeclarativeContainer):
    #Config del contenedor
    config = providers.Configuration()
   

    #Proveeddor de dependencias
    getLibroUseCase = providers.Singleton(GetLibroUseCase)