from dependency_injector import containers, providers
from ..domain.usecases.obtenerActividadesUsuarioUseCase import ObtenerActividadesUsuarioUseCase,ObtenerActividadesKantUseCase
from ..domain.usecases.crearActividadUseCase import CrearActividadUseCase

class ActividadesUseCaseContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    obtenerActividadesUsuarioUseCase = providers.Singleton(ObtenerActividadesUsuarioUseCase)

    crearActividadUseCase = providers.Singleton(CrearActividadUseCase)

    obtenerActividadesKantUseCase = providers.Singleton(ObtenerActividadesKantUseCase)
# class ObtenerEstructuraPeiUseCaseContainer(containers.DeclarativeContainer):

#     config = providers.Configuration()

#     obtenerEstructuraPeiUseCaseContainer = providers.Singleton(ObtenerEstructuraPeiUseCase)
