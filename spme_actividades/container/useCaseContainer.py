from dependency_injector import containers, providers
from ..domain.usecases.obtenerActividadesUsuarioUseCase import ObtenerActividadesUsuarioUseCase

class ActividadesUseCaseContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    obtenerActividadesUsuarioUseCase = providers.Singleton(ObtenerActividadesUsuarioUseCase)

# class ObtenerEstructuraPeiUseCaseContainer(containers.DeclarativeContainer):

#     config = providers.Configuration()

#     obtenerEstructuraPeiUseCaseContainer = providers.Singleton(ObtenerEstructuraPeiUseCase)
