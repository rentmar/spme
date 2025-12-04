from spme.common.MessageManager import MessageType

class ReponseMapper:
        
    @staticmethod
    def toSuccessResponse(response):
        return {
            "id": response.id,
            "mensaje": MessageType.SUCCESS.value,
        }
    
    @staticmethod
    def toSuccessResponseSolicitudViaje(response):
        return {
            "id": response.id,
            "mensaje": MessageType.SUCCESS.value,
            "numero_formulario": response.numeroFormulario,
        }
    
    @staticmethod
    def toRendicionesCuentasResponse(rendiciones):
        """
        Mapea una lista de objetos RendicionCuentas a formato de respuesta
        """
        from spme.common.MessageManager import MessageType
        
        if not rendiciones:
            return {
                "estado": MessageType.SUCCESS.value,
                "rendiciones": [],
                "mensaje": "No se encontraron rendiciones de cuentas"
            }
        
        resultado = []
        
        for rendicion in rendiciones:
            try:
                rendicion_data = {
                    "id": getattr(rendicion, 'id', None),
                    "numeroFormulario": getattr(rendicion, 'numeroFormulario', None),
                    "cpteDiario": getattr(rendicion, 'cpteDiario', None),
                    "fechaDesembolso": str(getattr(rendicion, 'fechaDesembolso', '')) if getattr(rendicion, 'fechaDesembolso', None) else None,
                    "montoAsignado": float(getattr(rendicion, 'montoAsignado', 0)) if getattr(rendicion, 'montoAsignado', None) else None,
                    "montoDescargado": float(getattr(rendicion, 'montoDescargado', 0)) if getattr(rendicion, 'montoDescargado', None) else None,
                    "saldo": float(getattr(rendicion, 'saldo', 0)) if getattr(rendicion, 'saldo', None) else None,
                    "detalleDestinoFondos": getattr(rendicion, 'detalleDestinoFondos', None),
                    "fechaActividadRC": str(getattr(rendicion, 'fechaActividadRC', '')) if getattr(rendicion, 'fechaActividadRC', None) else None,
                    "descripcionActividad": getattr(rendicion, 'descripcionActividad', None),
                    "lugarActividad": getattr(rendicion, 'lugarActividad', None),
                    "validacionResponsable": getattr(rendicion, 'validacionResponsable', False),
                    "validacionCoordinador": getattr(rendicion, 'validacionCoordinador', False),
                    "validacionContador": getattr(rendicion, 'validacionContador', False),
                    "validacionAdministrador": getattr(rendicion, 'validacionAdministrador', False),
                    "actividad_id": getattr(rendicion, 'actividad_id', None),
                    "tarea_id": getattr(rendicion, 'tarea_id', None),
                    "usuario_id": getattr(rendicion, 'usuario_id', None),
                    "bloquearIconos": getattr(rendicion, 'bloquearIconos', True),
                    "administrador_id": getattr(rendicion, 'administrador_id', None),
                    "contador_id": getattr(rendicion, 'contador_id', None),
                    "coordinador_id": getattr(rendicion, 'coordinador_id', None),
                    "responsable_id": getattr(rendicion, 'responsable_id', None),
                    "solicitudFondos_id": getattr(rendicion, 'solicitudFondos_id', None),
                    "solicitudReembolso_id": getattr(rendicion, 'solicitudReembolso_id', None),
                    "solicitudViaje_id": getattr(rendicion, 'solicitudViaje_id', None),
                    "solicitudPagoDirecto_id": getattr(rendicion, 'solicitudPagoDirecto_id', None),
                }
                
                resultado.append(rendicion_data)
                
            except Exception as e:
                print(f"Error mapeando rendicion {getattr(rendicion, 'id', 'unknown')}: {str(e)}")
                continue
        
        mensaje = f"Se encontraron {len(resultado)} rendiciones de cuentas"
        if len(resultado) == 1 and rendiciones[0].id:
            mensaje = f"Rendición de cuentas {rendiciones[0].id} encontrada exitosamente"
        
        return {
            "estado": MessageType.SUCCESS.value,
            "rendiciones": resultado,
            "mensaje": mensaje
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
                    "descripcion_actividad": getattr(solicitud, 'descripcion_actividad', None),
                    "objetivo_actividad": getattr(solicitud, 'objetivo_actividad', None),
                    "datos_forma_pago": getattr(solicitud, 'datos_forma_pago', None),
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
    def toSolicitudesReembolsoResponse(solicitudes):
        """
        Mapea una lista de objetos SolicitudReembolso a formato de respuesta
        """
        from spme.common.MessageManager import MessageType

        if not solicitudes:
            return {
                "estado": MessageType.SUCCESS.value,
                "solicitudes": [],
                "mensaje": "No se encontraron solicitudes de reembolso"
            }

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
                    "fechaDondeSeRealizoActividad": str(getattr(solicitud, 'fechaDondeSeRealizoActividad', '')) if getattr(solicitud, 'fechaDondeSeRealizoActividad', None) else None,
                    "descripcionReposicion": getattr(solicitud, 'descripcionReposicion', None),
                    "objetivoReposicion": getattr(solicitud, 'objetivoReposicion', None),
                    "validacionResponsable": getattr(solicitud, 'validacionResponsable', False),
                    "validacionCoordinador": getattr(solicitud, 'validacionCoordinador', False),
                    "responsable_id": getattr(solicitud, 'responsable_id', None),
                    "coordinador_id": getattr(solicitud, 'coordinador_id', None),
                    "usuario_id": getattr(solicitud, 'usuario_id', None),
                    "actividad_id": getattr(solicitud, 'actividad_id', None),
                    "tarea_id": getattr(solicitud, 'tarea_id', None),
                    "creado_el": str(getattr(solicitud, 'creado_el', '')) if getattr(solicitud, 'creado_el', None) else None,
                    "modificado_el": str(getattr(solicitud, 'modificado_el', '')) if getattr(solicitud, 'modificado_el', None) else None,
                }
                resultado.append(solicitud_data)
            except Exception as e:
                print(f"Error mapeando solicitud {getattr(solicitud, 'id', 'unknown')}: {str(e)}")
                continue

        mensaje = f"Se encontraron {len(resultado)} solicitudes de reembolso"
        if len(resultado) == 1 and solicitudes[0].id:
            mensaje = f"Solicitud de reembolso {solicitudes[0].id} encontrada exitosamente"

        return {
            "estado": MessageType.SUCCESS.value,
            "solicitudes": resultado,
            "mensaje": mensaje
        }
    
    @staticmethod
    def toFormasPagoResponse(formasPago):
        """
        Mapea una lista de objetos FormaPago a formato de respuesta
        """
        from spme.common.MessageManager import MessageType
        
        if not formasPago:
            return {
                "estado": MessageType.SUCCESS.value,
                "formasPago": [],
                "mensaje": "No se encontraron formas de pago"
            }
        
        resultado = []
        for formaPago in formasPago:
            try:
                formaPago_data = {
                    "id": getattr(formaPago, 'id', None),
                    "codigo": getattr(formaPago, 'codigo', None),  # CAMBIADO: nombre -> codigo
                    "formaPago": getattr(formaPago, 'formaPago', None),  # NUEVO CAMPO
                    # ELIMINADOS: nombre, descripcion, estado, fecha_creacion, fecha_actualizacion
                }
                resultado.append(formaPago_data)
            except Exception as e:
                print(f"Error mapeando forma de pago {getattr(formaPago, 'id', 'unknown')}: {str(e)}")
                continue
        
        mensaje = f"Se encontraron {len(resultado)} formas de pago"
        if len(resultado) == 1 and formasPago[0].id:
            mensaje = f"Forma de pago {formasPago[0].id} encontrada exitosamente"
        
        return {
            "estado": MessageType.SUCCESS.value,
            "formasPago": resultado,
            "mensaje": mensaje
        }
    
    @staticmethod
    def toSolicitudesViajeResponse(solicitudes):
        """
        Mapea una lista de objetos SolicitudViaje a formato de respuesta
        """
        from spme.common.MessageManager import MessageType

        if not solicitudes:
            return {
                "estado": MessageType.SUCCESS.value,
                "solicitudes": [],
                "mensaje": "No se encontraron solicitudes de viaje"
            }

        resultado = []
        for solicitud in solicitudes:
            try:
                solicitud_data = {
                    "id": getattr(solicitud, 'id', None),
                    "numeroFormulario": getattr(solicitud, 'numeroFormulario', None),
                    "evento": getattr(solicitud, 'evento', None),
                    "lugarEvento": getattr(solicitud, 'lugarEvento', None),
                    "institucionesParticipantes": getattr(solicitud, 'institucionesParticipantes', None),
                    "organizador": getattr(solicitud, 'organizador', None),
                    "quienCubreGastos": getattr(solicitud, 'quienCubreGastos', None),
                    "justificacionAsistencia": getattr(solicitud, 'justificacionAsistencia', None),
                    "fondosUnitas": getattr(solicitud, 'fondosUnitas', None),
                    "tareasPrevias": getattr(solicitud, 'tareasPrevias', None),
                    "formaPago_id": getattr(solicitud, 'formaPago_id', None),
                    "montoSolicitado": float(getattr(solicitud, 'montoSolicitado', 0)) if getattr(solicitud, 'montoSolicitado', None) else None,
                    "lugarSolicitud": getattr(solicitud, 'lugarSolicitud', None),
                    "fechaSolicitud": str(getattr(solicitud, 'fechaSolicitud', '')) if getattr(solicitud, 'fechaSolicitud', None) else None,
                    "fechaEvento": str(getattr(solicitud, 'fechaEvento', '')) if getattr(solicitud, 'fechaEvento', None) else None,
                    "detalleGasto": getattr(solicitud, 'detalleGasto', None),
                    "validacionResponsable": getattr(solicitud, 'validacionResponsable', False),
                    "validacionCoordinador": getattr(solicitud, 'validacionCoordinador', False),
                    "responsable_id": getattr(solicitud, 'responsable_id', None),
                    "coordinador_id": getattr(solicitud, 'coordinador_id', None),
                    "usuario_id": getattr(solicitud, 'usuario_id', None),
                    "actividad_id": getattr(solicitud, 'actividad_id', None),
                    "tarea_id": getattr(solicitud, 'tarea_id', None),
                    "bloquearIconos": getattr(solicitud, 'bloquearIconos', True),
                }
                resultado.append(solicitud_data)
            except Exception as e:
                print(f"Error mapeando solicitud {getattr(solicitud, 'id', 'unknown')}: {str(e)}")
                continue

        mensaje = f"Se encontraron {len(resultado)} solicitudes de viaje"
        if len(resultado) == 1 and solicitudes[0].id:
            mensaje = f"Solicitud de viaje {solicitudes[0].id} encontrada exitosamente"

        return {
            "estado": MessageType.SUCCESS.value,
            "solicitudes": resultado,
            "mensaje": mensaje
        }
    
    @staticmethod
    def toSolicitudesPagoDirectoResponse(solicitudes):
        """
        Mapea una lista de objetos SolicitudPagoDirecto a formato de respuesta
        """
        from spme.common.MessageManager import MessageType

        if not solicitudes:
            return {
                "estado": MessageType.SUCCESS.value,
                "solicitudes": [],
                "mensaje": "No se encontraron solicitudes de pago directo"
            }

        resultado = []
        for solicitud in solicitudes:
            try:
                solicitud_data = {
                    "id": getattr(solicitud, 'id', None),
                    "numeroFormulario": getattr(solicitud, 'numeroFormulario', None),
                    "descripcion_actividad": getattr(solicitud, 'descripcion_actividad', None),
                    "fecha_realizacion": str(getattr(solicitud, 'fecha_realizacion', '')) if getattr(solicitud, 'fecha_realizacion', None) else None,
                    "objetivo_actividad": getattr(solicitud, 'objetivo_actividad', None),
                    "fuente_financiamiento": getattr(solicitud, 'fuente_financiamiento', None),
                    "detalleDestinoFondos": getattr(solicitud, 'detalleDestinoFondos', None),
                    "formaPago_id": getattr(solicitud, 'formaPago_id', None),
                    "lugarSolicitud": getattr(solicitud, 'lugarSolicitud', None),
                    "fechaSolicitud": str(getattr(solicitud, 'fechaSolicitud', '')) if getattr(solicitud, 'fechaSolicitud', None) else None,
                    "montoSolicitado": float(getattr(solicitud, 'montoSolicitado', 0)) if getattr(solicitud, 'montoSolicitado', None) else None,
                    "validacionResponsable": getattr(solicitud, 'validacionResponsable', False),
                    "validacionCoordinador": getattr(solicitud, 'validacionCoordinador', False),
                    "responsable_id": getattr(solicitud, 'responsable_id', None),
                    "coordinador_id": getattr(solicitud, 'coordinador_id', None),
                    "usuario_id": getattr(solicitud, 'usuario_id', None),
                    "actividad_id": getattr(solicitud, 'actividad_id', None),
                    "tarea_id": getattr(solicitud, 'tarea_id', None),
                    "bloquearIconos": getattr(solicitud, 'bloquearIconos', True),
                }
                resultado.append(solicitud_data)
            except Exception as e:
                print(f"Error mapeando solicitud {getattr(solicitud, 'id', 'unknown')}: {str(e)}")
                continue

        mensaje = f"Se encontraron {len(resultado)} solicitudes de pago directo"
        if len(resultado) == 1 and solicitudes[0].id:
            mensaje = f"Solicitud de pago directo {solicitudes[0].id} encontrada exitosamente"

        return {
            "estado": MessageType.SUCCESS.value,
            "solicitudes": resultado,
            "mensaje": mensaje
        }

    @staticmethod
    def toErrorResponse(errorMessage):
        return {
            "id":0,
            "numero_formulario": "",
            "objetivo_reposicion": "",
            "mensaje": errorMessage,
        }