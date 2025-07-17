from dependency_injector import containers, providers
from ..domain.repositories.solicitudFondosRepository import SolicitudFondosRepository

class SolicitudFondosRepositoryContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    solicitudFondosRepository = providers.Singleton(SolicitudFondosRepository)