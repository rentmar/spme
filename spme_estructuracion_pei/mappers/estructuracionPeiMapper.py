from ..common.MessageManager import MessageType

class EstructuracionPeiMapper:
        
    @staticmethod
    def toSuccessResponse(estructuraPeiResponse):
        return {
            "id": estructuraPeiResponse.id,
            "mensaje": MessageType.SUCCESS.value,
        }