from spme_autenticacion.container.repositoryContainer import UserRepositoryContainer

class ActualizarUsuarioUseCase:
    def __init__(self):
        self.contenedor = UserRepositoryContainer() 
        self.userRepository = self.contenedor.userRepository()

    def execute(self, userRequest):
        """Actualiza un usuario a partir del request."""
        return self.userRepository.actualizarUsuario(userRequest)
