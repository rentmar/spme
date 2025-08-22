from spme_autenticacion.container.repositoryContainer import UserRepositoryContainer

class ObtenerListaValidadoresUseCase:
    def __init__(self):
        self.contenedor = UserRepositoryContainer() 
        self.userRepository = self.contenedor.userRepository()

    def execute(self):
        """Obtiene la lista de validadores."""
        return self.userRepository.obtenerListaValidadores()
