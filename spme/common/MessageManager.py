from enum import Enum

class MessageType(Enum):
    INFO = "informacion"
    WARNING = "advertencia"
    ERROR = "error"
    SUCCESS = "exito"
    BAD_REQUEST = "peticion incorrecta"
    NOT_FOUND = "no encontrado"
    UNAUTHORIZED = "no autorizado"