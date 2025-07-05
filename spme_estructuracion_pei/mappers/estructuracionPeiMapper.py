from ..common.MessageManager import MessageType

class EstructuracionPeiMapper:
        
    @staticmethod
    def toSuccessResponse(estructuraPeiResponse):
        return {
            "id": estructuraPeiResponse.id,
            "mensaje": MessageType.SUCCESS.value,
        }
    
    @staticmethod
    def toEstructuraPeiResponse(estruncturaPei):
        return {
            "id": estruncturaPei.id,
            "titulo": estruncturaPei.titulo,
            "descripcion": estruncturaPei.descripcion,
            "fecha_creacion":estruncturaPei.fecha_creacion,
            "fecha_inicio":estruncturaPei.fecha_inicio,
            "fecha_fin":estruncturaPei.fecha_fin,
            "esta_vigente":estruncturaPei.esta_vigente,
            "creado_el":estruncturaPei.creado_el,
            "modificado_el":estruncturaPei.modificado_el
        }