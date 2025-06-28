from ..domain.models.request.userRequest import CreateUserRequest

class UserMapper:
    
    @staticmethod
    def toUserResponse(user):
        return {
            "id": user.id,
            "usuario": user.usuario,
            "password": user.password,
            "permisos": user.permisos,
        }
    
    @staticmethod
    def toUserEntity(userRequest):
        request = CreateUserRequest()
        request.usuario = userRequest['usuario']
        request.password = userRequest['password']      
        request.permisos = userRequest['permisos']
        return request
    
    @staticmethod
    def toSuccessResponse(user):
        return {
            "id": user.id,
            "mensaje": "",
        }