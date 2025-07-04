from dependency_injector import containers, providers
from ..domain.repositories.estructuraPeiRepository import EstructuracionPeiRepository

class EstructuracionPeiRepositoryContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    estructuracionPeiRepository = providers.Singleton(EstructuracionPeiRepository)