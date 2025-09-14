from spme_autenticacion.container.repositoryContainer import UserRepositoryContainer

class ActualizarEstadoUsuarioUseCase:
    def __init__(self):
        self.contenedor = UserRepositoryContainer() 
        self.userRepository = self.contenedor.userRepository()

    def execute(self, estadoRequest):
        """Cambia el estado de un usuario a partir del request."""
        return self.userRepository.actualizarEstadoUsuario(estadoRequest['id'], estadoRequest['is_active'])