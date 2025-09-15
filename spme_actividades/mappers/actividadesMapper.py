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
    def toActividadesGanttResponse(actividades):
        lista = []
        for actividad in actividades:
            act = {
                "codigo": actividad['codigo'],
                "nombre_corto": actividad['nombreCorto'],
                "descripcion": actividad['descripcion'],
                "tipo": actividad['tipo_id'],
                "fecha_programada": actividad['fecha_programada'],
                "fecha_inicio": actividad['fecha_inicio'],
                "fecha_cierre": actividad['fecha_cierre'],
                "grado_ejecucion": actividad['gradoEjecucion'],
                "estado": actividad['estado'],
            }
            lista.append(act)
        return {
            "estados":[
                {
                    "id": "PLAN",
                    "nombre": "Planificacion",
                    "color": "#64b5f6",
                },
                {
                    "id": "RETR",
                    "nombre": "Retraso",
                    "color": "#ff0000"
                },
                {
                    "id": "REPROG",
                    "nombre": "Reprogramacion",
                    "color": "#ffd54f"
                },
                {
                    "id": "EJEC",
                    "nombre": "En_Ejecucion",
                    "color": "#ffa726"
                },
                {
                    "id": "REP",
                    "nombre": "En_Reporte",
                    "color": "#81c784"
                },
                {
                    "id": "FIN",
                    "nombre": "Finalizado",
                    "color": "#003CFF"
                }
            ],
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
            "descripcion": encabezado.get('descripcion') if encabezado.get('descripcion') is not None else "No Definido",
            "estado": encabezado.get('estado'),
            "tipo": encabezado.get('tipo_actividad'),
            "fecha_programada": encabezado.get('fecha_programada'),
            "fecha_cierre": encabezado.get('fecha_cierre'),
            "presupuesto": encabezado.get('presupuesto') if encabezado.get('presupuesto') is not None else 0,
            "responsable": encabezado.get('nombre_responsable') if encabezado.get('nombre_responsable') is not None else "No Definido",
        }