from dependency_injector import containers, providers
from ..domain.usecases.obtenerActividadesUsuarioUseCase import ObtenerActividadesUsuarioUseCase
from ..domain.usecases.obtenerActividadesGantUseCase import ObtenerActividadesGantUseCase
from ..domain.usecases.obtenerEncabezadoActividadPorIdUseCase import ObtenerEncabezadoActividadPorIdUseCase
from ..domain.usecases.crearActividadUseCase import CrearActividadUseCase
from ..domain.usecases.obtenerActividadPorIdUseCase import ObtenerActividadPorIdUseCase

class ActividadesUseCaseContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    obtenerActividadesUsuarioUseCase = providers.Singleton(ObtenerActividadesUsuarioUseCase)

    crearActividadUseCase = providers.Singleton(CrearActividadUseCase)

    obtenerActividadesGantUseCase = providers.Singleton(ObtenerActividadesGantUseCase)

    obtenerActividadPorIdUseCase = providers.Singleton(ObtenerActividadPorIdUseCase)

    obtenerEncabezadoActividadPorIdUseCase = providers.Singleton(ObtenerEncabezadoActividadPorIdUseCase)
