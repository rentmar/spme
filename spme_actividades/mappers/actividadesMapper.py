from ..common.MessageManager import MessageType

class ActividadesMapper:
    @staticmethod
    def toSuccessResponse(actividadesResponse):
        return {
            "id": actividadesResponse.id,
            "mensaje": MessageType.SUCCESS.value,
        }
    
    @staticmethod
    def toErrorResponse(errorMessage):
        return {
            "id": 0,
            "mensaje": errorMessage
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
    
    @staticmethod
    def toActividadesKantResponse(actividades):
        lista = []
        for actividad in actividades:
            act = {
                "codigo": actividad['codigo'],
                "descripcion": actividad['descripcion'],
                "tipo": actividad['tipo'],
                "fecha_programada": actividad['fecha_programada'],
                "duracion": actividad['duracion'],
                "fecha_inicio": actividad['fecha_inicio'],
                "fecha_cierre": actividad['fecha_cierre'],
                "estado": actividad['estado'],
            }
            lista.append(act)
        return {
            "actividades": lista
        }

    @staticmethod
    def toObtenerActividadIdResponse(actividad):
        return {
            "id": actividad.id,
            "codigo": actividad.codigo,
            "descripcion": actividad.descripcion,
            "tipo": actividad.tipo,
            "fecha_programada": actividad.fecha_programada,
            "duracion": actividad.duracion,
            "fecha_inicio": actividad.fecha_inicio,
            "fecha_cierre": actividad.fecha_cierre,
            "estado": actividad.estado,
        }

    @staticmethod
    def toObtenerEncabezadoActividadResponse(encabezado):
        return {
            "codigo": encabezado.get('codigo'),
            "descripcion": encabezado.get('descripcion'),
            "estado": encabezado.get('estado'),
            "tipo": encabezado.get('tipo_actividad'),
            "fecha_programada": encabezado.get('fecha_programada'),
            "fecha_cierre": encabezado.get('fecha_cierre'),
            "presupuesto": encabezado.get('presupuesto'),
            "responsable": {"nombre": encabezado.get('nombre_responsable')} if 'nombre_responsable' in encabezado else None,
        }