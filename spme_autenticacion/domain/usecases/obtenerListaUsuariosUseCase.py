from spme_autenticacion.container.repositoryContainer import UserRepositoryContainer

class ObtenerListaUsuariosUseCase:
    def __init__(self):
        self.contenedor = UserRepositoryContainer() 
        self.userRepository = self.contenedor.userRepository()

    def execute(self):
        """Obtiene la lista de usuarios."""
        return self.userRepository.obtenerListaUsuarios()
