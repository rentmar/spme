from dependency_injector import containers, providers
from ..domain.usecases.crearEstructuraPeiUseCase import CrearEstructuraPeiUseCase

class CrearEstructuraPeiUseCaseContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    crearEstructuraPeiUseCase = providers.Singleton(CrearEstructuraPeiUseCase)


