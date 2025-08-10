from spme.common.MessageManager import MessageType

class ReponseMapper:
        
    @staticmethod
    def toSuccessResponse(response):
        return {
            "id": response.id,
            "mensaje": MessageType.SUCCESS.value,
        }
    
    @staticmethod
    def toSolicitudFondosResponse(solicitudFondos):
        return {
            "id": solicitudFondos.id,
            "titulo": solicitudFondos.titulo,
            "descripcion": solicitudFondos.descripcion,
            "fecha_creacion":solicitudFondos.fecha_creacion,
            "fecha_inicio":solicitudFondos.fecha_inicio,
            "fecha_fin":solicitudFondos.fecha_fin,
            "esta_vigente":solicitudFondos.esta_vigente,
            "creado_el":solicitudFondos.creado_el,
            "modificado_el":solicitudFondos.modificado_el
        }
    
    @staticmethod
    def toErrorResponse(errorMessage):
        return {
            "id":0,
            "mensaje": errorMessage,
        }