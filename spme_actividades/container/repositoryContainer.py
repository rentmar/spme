from dependency_injector import containers, providers
from ..domain.repositories.actividadesRespository import ActividadesRepository

class ActividadesRepositoryContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    actividadesRepository = providers.Singleton(ActividadesRepository)