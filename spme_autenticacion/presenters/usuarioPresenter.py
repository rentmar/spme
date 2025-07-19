from spme_autenticacion.container.useCaseContainer import UserUseCaseContainer
from spme_autenticacion.mappers.userMapper import UserMapper

class UsuarioPresenter:
    def __init__(self):
        self.contenedor = UserUseCaseContainer()
        self.userUseCase = self.contenedor.getUserUseCase()
        self.createUserUseCase = self.contenedor.createUserUseCase()
        self.autenticarUsuarioUseCase = self.contenedor.autenticarUsuarioUseCase()
        self.obtenerUsuariosUseCase = self.contenedor.obtenerUsuariosUseCase()

    def obtenerUsuario(self,userRequest):
        """
        Obtiene el usuario a partir de la solicitud.
        """
        usuario = self.userUseCase.execute(userRequest)
        
        if usuario is not None:
            return UserMapper.toUsuarioResponse(usuario)
        else:
            return UserMapper.toErrorResponse("Usuario no encontrado")
        
    def createUsuario(self, userRequest):
        """
        Crea un nuevo usuario a partir de la solicitud.
        """
        usuario = self.createUserUseCase.execute(userRequest)

        if usuario is not None:
            return UserMapper.toSuccessResponse(usuario)
        else:
            return UserMapper.toErrorResponse("Error al crear el usuario")
        
    def obtenerListaUsuarios(self):
        """
        Obtiene la lista de usuarios.
        """
        lista = self.obtenerUsuariosUseCase.execute()
        print("Lista de usuarios obtenida:", lista)
        return None#UserMapper.toListResponse(lista)

    def autenticarUsuario(self, userRequest):
        """
        Autentica un usuario a partir de la solicitud.
        """
        usuario = self.autenticarUsuarioUseCase.execute(userRequest)
        
        if usuario is not None:
            return UserMapper.toAutenticacionSuccessResponse(usuario)
        else:
            return UserMapper.toAutenticacionErrorResponse("Credenciales inválidas")