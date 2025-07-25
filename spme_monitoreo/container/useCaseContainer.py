from dependency_injector import containers, providers
from ..domain.usecases.solicitudFondosUseCase import CrearSolicitudFondosUseCase
from ..domain.usecases.rendicionCuentasUseCase import CrearRendicionCuentasUseCase
from ..domain.usecases.solicitudReembolsoUseCase import CrearSolicitudReembolsoUseCase

class CrearSolicitudFondosUseCaseContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    crearSolicitudFondosUseCase = providers.Singleton(CrearSolicitudFondosUseCase)

class CrearRendicionCuentasUseCaseContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    crearRendicionCuentasUseCase = providers.Singleton(CrearRendicionCuentasUseCase)

class CrearSolicitudReembolsoUseCaseContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    crearSolicitudReembolsoUseCase = providers.Singleton(CrearSolicitudReembolsoUseCase)
