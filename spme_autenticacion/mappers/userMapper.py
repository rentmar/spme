from ..domain.models.request.userRequest import CrearUsuarioRequest
from spme.common.MessageManager import MessageType

class UserMapper:
    
    @staticmethod
    def toUsuarioResponse(user):
        return {
            "id": 1,
            "usuario": "ACarvajal",
            "nombre": "Alejandro",
            "paterno": "Carvajal",
            "materno": "Carvajal",
            "ci": "4859687",
            "cargo": "Gerente",
            "banco": "Banco Nacional Bolivia BNB",
            "numeroCuenta": "5874-55212-1211-15-4",
            "tipoCuenta": "AHORRO"
        }
        # return {
        #     "id": user.id,
        #     "usuario": user.username,
        #     "nombre": user.nombre,
        #     "paterno": user.paterno,
        #     "materno": user.materno,
        #     "permisos": user.permisos,
        #     "activo": user.is_active
        # }
    
    # @staticmethod
    # def toUserEntity(userRequest):
    #     request = CreateUserRequest()
    #     request.usuario = userRequest['username']
    #     request.password = userRequest['password']      
    #     request.permisos = userRequest['permisos']
    #     return request
    
    @staticmethod
    def toCreateSuccessResponse(user):
        return {
            "id": user.id,
            "mensaje": MessageType.SUCCESS.value,
        }
    
    @staticmethod
    def toErrorResponse(error_message):
        return {
            "id":0,
            "mensaje": error_message,
        }
    
    @staticmethod
    def toAutenticacionSuccessResponse(user):
        return {
            "validacion": True,
            "mensaje": MessageType.AUTHORIZED.value,
            "usuario": user.username,
            "permisos":user.permisos
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