from dependency_injector import containers, providers
from ..domain.usecases.crearEstructuraPeiUseCase import CrearEstructuraPeiUseCase,ObtenerEstructuraPeiUseCase

class CrearEstructuraPeiUseCaseContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    crearEstructuraPeiUseCase = providers.Singleton(CrearEstructuraPeiUseCase)

    obtenerEstructuraPeiUseCaseContainer = providers.Singleton(ObtenerEstructuraPeiUseCase)

# class ObtenerEstructuraPeiUseCaseContainer(containers.DeclarativeContainer):

#     config = providers.Configuration()

#     obtenerEstructuraPeiUseCaseContainer = providers.Singleton(ObtenerEstructuraPeiUseCase)
