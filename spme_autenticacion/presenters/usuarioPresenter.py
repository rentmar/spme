from spme_autenticacion.container.useCaseContainer import UserUseCaseContainer
from spme_autenticacion.mappers.userMapper import UserMapper

class UsuarioPresenter:
    def __init__(self):
        self.contenedor = UserUseCaseContainer()
        self.userUseCase = self.contenedor.getUserUseCase()
        self.createUserUseCase = self.contenedor.createUserUseCase()
        self.autenticarUsuarioUseCase = self.contenedor.autenticarUsuarioUseCase()

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
        userRequestEntity = UserMapper.toSuccessResponse(userRequest)

        usuario = self.createUserUseCase.execute(userRequestEntity)
        if usuario is not None:
            return UserMapper.toSuccessResponse(usuario)
        else:
            return UserMapper.toErrorResponse("Error al crear el usuario")
        
    def autenticarUsuario(self, userRequest):
        """
        Autentica un usuario a partir de la solicitud.
        """
        usuario = self.autenticarUsuarioUseCase.execute(userRequest)
        
        if usuario is not None:
            return UserMapper.toAutenticacionSuccessResponse(usuario)
        else:
            return UserMapper.toAutenticacionErrorResponse("Credenciales inválidas")