from spme_autenticacion.container.repositoryContainer import UserRepositoryContainer
class GetUserUseCase:
    def __init__(self):
        self.contenedor = UserRepositoryContainer() 
        self.userRepository = self.contenedor.userRepository()

    def execute(self, userRequest):
        """Obtiene un usuario por su nombre de usuario del request user_name."""
        return self.userRepository.getUserByName(userRequest['usuario'])
    
class CreateUserUseCase:
    def __init__(self):
        self.contenedor = UserRepositoryContainer() 
        self.userRepository = self.contenedor.userRepository()

    def execute(self, userEntity):
        """Crea un nuevo usuario a partir del request."""
        return self.userRepository.createUser(userEntity)