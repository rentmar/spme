from spme_autenticacion.container.useCaseContainer import UserUseCaseContainer
from spme_autenticacion.mappers.userMapper import UserMapper

class UsuarioPresenter:
    def __init__(self):
        self.contenedor = UserUseCaseContainer()
        self.userUseCase = self.contenedor.getUserUseCase()
        self.createUserUseCase = self.contenedor.createUserUseCase()

    def getUsuario(self,userRequest):
        """
        Obtiene el usuario a partir de la solicitud.
        """
        usuario = self.userUseCase.execute(userRequest)
        if usuario is not None:
            return UserMapper.toUserResponse(usuario)
        else:
            return None
        
    def createUsuario(self, userRequest):
        """
        Crea un nuevo usuario a partir de la solicitud.
        """
        userRequestEntity = UserMapper.toUserEntity(userRequest)
        usuario = self.createUserUseCase.execute(userRequestEntity)
        if usuario is not None:
            return UserMapper.toSuccessResponse(usuario)
        else:
            return None