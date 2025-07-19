from ..domain.models.request.userRequest import CrearUsuarioRequest
from spme.common.MessageManager import MessageType

class UserMapper:
    
    @staticmethod
    def toUsuarioResponse(user):
        return {
            "id": user.id,
            "usuario": user.username,
            "nombre": user.nombre,
            "paterno": user.paterno,
            "materno": user.materno,
            "permisos": user.permisos,
            "activo": user.is_active
        }
    
    # @staticmethod
    # def toUserEntity(userRequest):
    #     request = CreateUserRequest()
    #     request.usuario = userRequest['username']
    #     request.password = userRequest['password']      
    #     request.permisos = userRequest['permisos']
    #     return request
    
    @staticmethod
    def toSuccessResponse(user):
        return {
            "id": user.id,
            "mensaje": MessageType.SUCCESS.value,
        }
    
    @staticmethod
    def toErrorResponse(error_message):
        return {
            "mensaje": error_message,
        }
    
    @staticmethod
    def toAutenticacionSuccessResponse(user):
        return {
            "validacion": True,
            "mensaje": MessageType.SUCCESS.value,
            "usuario": UserMapper.toUsuarioResponse(user)
        }

    @staticmethod
    def toAutenticacionErrorResponse(error_message):
        return {
            "validacion": False,
            "mensaje": error_message,
        }
    

    @staticmethod
    def toListResponse(lista):
        """
        Convierte una lista de usuarios a un formato de respuesta.
        """
        return {
            "usuarios": [UserMapper.toUsuarioResponse(user) for user in lista]
        }