from dependency_injector import containers, providers
from ..domain.usecases.userUseCase import GetUserUseCase, CreateUserUseCase,AutenticarUsuarioUseCase
from ..domain.usecases.obtenerListaUsuariosUseCase import ObtenerListaUsuariosUseCase
from ..domain.usecases.actualizarUsuarioUseCase import ActualizarUsuarioUseCase
from ..domain.usecases.obtenerListaValidadoresUseCase import ObtenerListaValidadoresUseCase 
from ..domain.usecases.actualizarEstadoUsuarioUseCase import ActualizarEstadoUsuarioUseCase
from ..domain.usecases.actualizarPasswordUsuarioUseCase import ActualizarPasswordUsuarioUseCase

class UserUseCaseContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    getUserUseCase = providers.Singleton(GetUserUseCase)

    createUserUseCase = providers.Singleton(CreateUserUseCase)

    autenticarUsuarioUseCase = providers.Singleton(AutenticarUsuarioUseCase)

    obtenerUsuariosUseCase = providers.Singleton(ObtenerListaUsuariosUseCase)

    obtenerListaValidadoresUseCase = providers.Singleton(ObtenerListaValidadoresUseCase)

    actualizarUsuarioUseCase = providers.Singleton(ActualizarUsuarioUseCase)

    actualizarEstadoUseCase = providers.Singleton(ActualizarEstadoUsuarioUseCase)

    actualizarPasswordUseCase = providers.Singleton(ActualizarPasswordUsuarioUseCase)

