from spme_autenticacion.container.repositoryContainer import UserRepositoryContainer

class ActualizarPasswordUsuarioUseCase:
    def __init__(self):
        self.contenedor = UserRepositoryContainer() 
        self.userRepository = self.contenedor.userRepository()

    def execute(self, resetRequest):
        """Cambia el password de un usuario a partir del request."""
        return self.userRepository.actualizarPasswordUsuario(resetRequest['id'], resetRequest['password'])