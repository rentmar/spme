from ..domain.models.request.userRequest import CrearUsuarioRequest
from spme.common.MessageManager import MessageType 

class UserMapper:
    
    @staticmethod
    def toCreateSuccessResponse(user):
        return {
            "id": user.id,
            "mensaje": MessageType.SUCCESS.value,
        }
    
    @staticmethod
    def toUpdateSuccessResponse(user):
        return {
            "usuario": user.username,
            "mensaje": MessageType.UPDATE.value,
        }
    
    @staticmethod
    def toErrorResponse(error_message):
        return {
            "usuario": "",
            "mensaje": error_message,
        }
    
    @staticmethod
    def toAutenticacionSuccessResponse(user):
        return {
            "id": user.id,
            "validacion": True,
            "mensaje": MessageType.AUTHORIZED.value,
            "usuario": user.username,
            "rol":user.cargo,
            "permisos": user.permisos,
            "id": user.id,
        }
        print(f"🟠 [UserMapper] Construyendo respuesta: {response_data}")  # ← LOG
        return response_data

    @staticmethod
    def toAutenticacionErrorResponse(error_message):
        return {
            "validacion": False,
            "mensaje": error_message,
        }
    

    @staticmethod
    def toValidadorResponse(user): 
        return {
            "id": user.get("id"),
            "nombre": user.get("nombre"),
            "paterno": user.get("paterno"),
            "materno": user.get("materno"),
            "cargo": user.get("cargo"),
        }

    @staticmethod
    def toListValidadoresResponse(lista):
        return {
            "validadores": [UserMapper.toValidadorResponse(user) for user in lista]
        }

    @staticmethod
    def toUsuarioResponse(user):
        return {
            "id": user.get("id"),
            "usuario": user.get("username"),
            "nombre": user.get("nombre"),
            "paterno": user.get("paterno"),
            "materno": user.get("materno"),
            "correo": user.get("correo"),
            "ci": user.get("ci"),
            "cargo": user.get("cargo"),
            "permisos": user.get("permisos"),
            "banco": user.get("banco"),
            "numero_cuenta": user.get("numero_cuenta"),
            "tipo_cuenta": user.get("tipo_cuenta"),
            "es_activo": user.get("is_active"),
        }
    
    @staticmethod
    def toListUserResponse(lista):
        """
        Convierte una lista de usuarios a un formato de respuesta.
        """
        return {
            "usuarios": [UserMapper.toUsuarioResponse(user) for user in lista]
        }