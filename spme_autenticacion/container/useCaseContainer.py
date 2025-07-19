from dependency_injector import containers, providers
from ..domain.usecases.userUseCase import GetUserUseCase, CreateUserUseCase,AutenticarUsuarioUseCase,ObtenerUsuariosUseCase

class UserUseCaseContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    getUserUseCase = providers.Singleton(GetUserUseCase)

    createUserUseCase = providers.Singleton(CreateUserUseCase)

    autenticarUsuarioUseCase = providers.Singleton(AutenticarUsuarioUseCase)

    obtenerUsuariosUseCase = providers.Singleton(ObtenerUsuariosUseCase)

