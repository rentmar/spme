from dependency_injector import containers, providers
from ..domain.repositories.userRepository import UserRepository

class UserRepositoryContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    userRepository = providers.Singleton(UserRepository)