from dependency_injector import containers, providers
from ..domain.repositories.proyectoRepository import ProyectoRepository

class ProyectoRepositoryContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    proyectoRepository = providers.Singleton(ProyectoRepository)