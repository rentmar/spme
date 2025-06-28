from dependency_injector import containers, providers
from ..domain.usecases.getUserUseCase import GetUserUseCase, CreateUserUseCase

class UserUseCaseContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    getUserUseCase = providers.Singleton(GetUserUseCase)

    createUserUseCase = providers.Singleton(CreateUserUseCase)

