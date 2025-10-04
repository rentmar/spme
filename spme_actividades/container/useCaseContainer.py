from dependency_injector import containers, providers
from ..domain.usecases.obtenerActividadesUsuarioUseCase import ObtenerActividadesUsuarioUseCase
from ..domain.usecases.obtenerActividadesGanttUseCase import ObtenerActividadesGanttUseCase
from ..domain.usecases.obtenerEncabezadoActividadPorIdUseCase import ObtenerEncabezadoActividadPorIdUseCase
from ..domain.usecases.crearActividadUseCase import CrearActividadUseCase
from ..domain.usecases.obtenerActividadPorIdUseCase import ObtenerActividadPorIdUseCase
from ..domain.usecases.obtenerDashboardActividadUseCase import ObtenerDashboardActividadUseCase

class ActividadesUseCaseContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    obtenerActividadesUsuarioUseCase = providers.Singleton(ObtenerActividadesUsuarioUseCase)

    crearActividadUseCase = providers.Singleton(CrearActividadUseCase)

    obtenerActividadesGanttUseCase = providers.Singleton(ObtenerActividadesGanttUseCase)

    obtenerActividadPorIdUseCase = providers.Singleton(ObtenerActividadPorIdUseCase)

    obtenerEncabezadoActividadPorIdUseCase = providers.Singleton(ObtenerEncabezadoActividadPorIdUseCase)

    obtenerDashboardAvtividadUseCase = providers.Singleton(ObtenerDashboardActividadUseCase)
