from dependency_injector import containers, providers
from ..domain.repositories.solicitudFondosRepository import SolicitudFondosRepository
from ..domain.repositories.rendicionCuentasRepository import RendicionCuentasRepository
from ..domain.repositories.solicitudReembolsoRepository import SolicitudReembolsoRepository

class SolicitudFondosRepositoryContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    solicitudFondosRepository = providers.Singleton(SolicitudFondosRepository)

class RendicionCuentasRepositoryContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    rendicionCuentasRepository = providers.Singleton(RendicionCuentasRepository)

class SolicitudReembolsoRepositoryContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    solicitudReembolsoRepository = providers.Singleton(SolicitudReembolsoRepository)