from ..common.MessageManager import MessageType

class ActividadesMapper:
    @staticmethod
    def toSuccessResponse(actividadesResponse):
        return {
            "id": actividadesResponse.id,
            "mensaje": MessageType.SUCCESS.value,
        }

    @staticmethod
    def toActividadesUsuarioResponse(actividades):
        lista = []
        for actividad in actividades:
            act = {
                "id": actividad.id,
                "codigo": actividad.codigo,
                "descripcion": actividad.descripcion,
                "tipo": actividad.tipo,
                "fecha_programada": actividad.fecha_programada,
                "duracion": actividad.duracion,
                "fecha_inicio": actividad.fecha_inicio,
                "fecha_cierre": actividad.fecha_cierre,
                "presupuesto": actividad.presupuesto,
                "presupuesto_pei": actividad.presupuesto_pei,
                "estado": actividad.estado,
                "procedencia_fondos": actividad.procedencia_fondos,
                "objetivo_de_actividad": actividad.objetivo_de_actividad,
                "descripcion_evaluacion": actividad.descripcion_evaluacion,
                "justificacion_modificacion": actividad.justificacion_modificacion,
                "datos_actividad": actividad.datos_actividad,
            }
            lista.append(act)
        return {
            "actividades": lista
        }
