from dependency_injector import containers, providers
from ..domain.usecases.obtenerActividadesUsuarioUseCase import ObtenerActividadesUsuarioUseCase,ObtenerActividadesKantUseCase
from ..domain.usecases.obtenerEncabezadoActividadPorIdUseCase import ObtenerEncabezadoActividadPorIdUseCase
from ..domain.usecases.crearActividadUseCase import CrearActividadUseCase
from ..domain.usecases.obtenerActividadPorIdUseCase import ObtenerActividadPorIdUseCase

class ActividadesUseCaseContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    obtenerActividadesUsuarioUseCase = providers.Singleton(ObtenerActividadesUsuarioUseCase)

    crearActividadUseCase = providers.Singleton(CrearActividadUseCase)

    obtenerActividadesKantUseCase = providers.Singleton(ObtenerActividadesKantUseCase)

    obtenerActividadPorIdUseCase = providers.Singleton(ObtenerActividadPorIdUseCase)

    obtenerEncabezadoActividadPorIdUseCase = providers.Singleton(ObtenerEncabezadoActividadPorIdUseCase)
