from spme.common.MessageManager import MessageType

class SolicitudFondosMapper:
        
    @staticmethod
    def toSuccessResponse(solicitudFondosResponse):
        return {
            "id": solicitudFondosResponse.id,
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
            "mensaje": MessageType.ERROR.value,
            "error": errorMessage
        }