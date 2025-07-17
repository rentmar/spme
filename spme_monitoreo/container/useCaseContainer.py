from dependency_injector import containers, providers
from ..domain.usecases.solicitudFondosUseCase import CrearSolicitudFondosUseCase

class CrearSolicitudFondosUseCaseContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    crearSolicitudFondosUseCase = providers.Singleton(CrearSolicitudFondosUseCase)
