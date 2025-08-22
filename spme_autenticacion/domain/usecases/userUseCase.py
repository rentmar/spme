from spme_autenticacion.container.repositoryContainer import UserRepositoryContainer
class GetUserUseCase:
    def __init__(self):
        self.contenedor = UserRepositoryContainer() 
        self.userRepository = self.contenedor.userRepository()

    def execute(self, username):
        """Obtiene un usuario por su nombre de usuario del request user_name."""
        return self.userRepository.obtenerUsuarioPorUsername(username)

class CreateUserUseCase:
    def __init__(self):
        self.contenedor = UserRepositoryContainer() 
        self.userRepository = self.contenedor.userRepository()

    def execute(self, userRequest):
        """Crea un nuevo usuario a partir del request."""
        return self.userRepository.createUser(userRequest)

class AutenticarUsuarioUseCase:
    def __init__(self):
        self.contenedor = UserRepositoryContainer() 
        self.userRepository = self.contenedor.userRepository()

    def execute(self, userRequest):
        """Autentica un usuario a partir del request."""
        return self.userRepository.autenticarUsuario(userRequest)
    
class ObtenerUsuariosUseCase:
    def __init__(self):
        self.contenedor = UserRepositoryContainer() 
        self.userRepository = self.contenedor.userRepository()

    def execute(self):
        """Obtiene la lista de usuarios."""
        usuarios = self.userRepository.obtenerListaUsuarios()
        return list(usuarios.values())