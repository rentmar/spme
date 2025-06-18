from dependency_injector import containers, providers
from ..domain.repositories.ObjetivoEspecificoRepository import ObjetivoEspecificoRepository

class ObjetivoEspecificoRepositoryContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    objetivoEspecificoRepository = providers.Singleton(ObjetivoEspecificoRepository)
