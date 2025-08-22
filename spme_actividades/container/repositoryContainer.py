from dependency_injector import containers, providers
from ..domain.repositories.actividadesRespository import ActividadesRepository
from ..domain.repositories.actividadTipoRepository import ActividadTipoRepository

class ActividadesRepositoryContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    actividadesRepository = providers.Singleton(ActividadesRepository)

class ActividadTipoRepositoryContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    actividadTipoRepository = providers.Singleton(ActividadTipoRepository)