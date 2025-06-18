from dependency_injector import containers, providers
from ..domain.usecases.ObjetivoEspecificoUseCase import ObjetivoEspecificoUseCase

class ObjetivoEspecificoUseCaseContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    objetivoEspecificoUseCase = providers.Singleton(ObjetivoEspecificoUseCase)