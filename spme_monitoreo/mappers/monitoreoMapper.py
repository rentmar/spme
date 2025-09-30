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
    def toSolicitudesFondosResponse(solicitudes):
        """
        Mapea una lista de objetos SolicitudFondos a formato de respuesta
        de manera segura, manejando campos faltantes.
        """
        resultado = []
        
        for solicitud in solicitudes:
            try:
                solicitud_data = {
                    "id": getattr(solicitud, 'id', None),
                    "numeroFormulario": getattr(solicitud, 'numeroFormulario', None),
                    "detalleDestinoFondos": getattr(solicitud, 'detalleDestinoFondos', None),
                    "formaPago_id": getattr(solicitud, 'formaPago_id', None),
                    "lugarSolicitud": getattr(solicitud, 'lugarSolicitud', None),
                    "fechaSolicitud": str(getattr(solicitud, 'fechaSolicitud', '')) if getattr(solicitud, 'fechaSolicitud', None) else None,
                    "montoSolicitado": float(getattr(solicitud, 'montoSolicitado', 0)) if getattr(solicitud, 'montoSolicitado', None) else None,
                    "validacionResponsable": getattr(solicitud, 'validacionResponsable', False),
                    "responsable_id": getattr(solicitud, 'responsable_id', None),
                    "validacionCoordinador": getattr(solicitud, 'validacionCoordinador', False),
                    "coordinador_id": getattr(solicitud, 'coordinador_id', None),
                    "usuario_id": getattr(solicitud, 'usuario_id', None),
                    "actividad_id": getattr(solicitud, 'actividad_id', None),
                    "tarea_id": getattr(solicitud, 'tarea_id', None),
                    "fechaRealizacionActividad": str(getattr(solicitud, 'fechaRealizacionActividad', '')) if getattr(solicitud, 'fechaRealizacionActividad', None) else None,
                    "bloquearIconosSolFondos": getattr(solicitud, 'bloquearIconosSolFondos', True),
                }
                
                # Campos de auditoría (manejo seguro)
                for campo_fecha in ['creado_el', 'created_at', 'modificado_el', 'updated_at']:
                    if hasattr(solicitud, campo_fecha):
                        valor = getattr(solicitud, campo_fecha)
                        if valor:
                            nombre_campo_respuesta = 'creado_el' if 'creat' in campo_fecha else 'modificado_el'
                            solicitud_data[nombre_campo_respuesta] = valor.isoformat()
                
                # Asegurar que existan los campos esperados en la respuesta
                if 'creado_el' not in solicitud_data:
                    solicitud_data['creado_el'] = None
                if 'modificado_el' not in solicitud_data:
                    solicitud_data['modificado_el'] = None
                    
                resultado.append(solicitud_data)
                
            except Exception as e:
                # En caso de error con una solicitud, continuar con las demás
                print(f"Error mapeando solicitud {getattr(solicitud, 'id', 'unknown')}: {str(e)}")
                continue
        
        return resultado
    
    @staticmethod
    def toErrorResponse(errorMessage):
        return {
            "id":0,
            "mensaje": errorMessage,
        }