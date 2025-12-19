import json
from spme_monitoreo.container.useCaseContainer import (
    CrearSolicitudFondosUseCaseContainer,
    ActualizarValidacionSolicitudFondosUseCaseContainer,
    ActualizarValidacionRendicionCuentasUseCaseContainer,
    ActualizarValidacionSolicitudReembolsoUseCaseContainer,
    ActualizarValidacionSolicitudViajeUseCaseContainer,
    ActualizarValidacionSolicitudPagoDirectoUseCaseContainer, 
    CrearRendicionCuentasUseCaseContainer,
    CrearSolicitudReembolsoUseCaseContainer,
    CrearSolicitudViajeUseCaseContainer,
    CrearSolicitudPagoDirectoUseCaseContainer,
    ObtenerDatosFormularioUseCaseContainer,
    FormaPagoUseCaseContainer)
from spme_monitoreo.mappers.monitoreoMapper import ReponseMapper

class SolicitudFondosPresenter:
    def __init__(self):
        self.useCaseContainer = CrearSolicitudFondosUseCaseContainer()
        self.crearSolicitudFondosUseCase = self.useCaseContainer.crearSolicitudFondosUseCase()

    # def crearSolicitudFondos(self, requestData):
    #     crearSolicitud = self.crearSolicitudFondosUseCase.execute(requestData)
    #     if crearSolicitud is not None:
    #         return ReponseMapper.toSuccessResponse(crearSolicitud)
    #     else:
    #         return ReponseMapper.toErrorResponse("Error al crear la solicitud de fondos")
    
    def crearSolicitudFondos(self, requestData):
            """
            Mapea el payload del frontend a los nombres de campos del modelo
            y llama al caso de uso para crear la solicitud de fondos.
            """
            try:
                # No es necesario deserializar si viene del serializer validated_data, ya son dicts
                detalleDestinoFondos = requestData.get('detalleDestinoFondos', {})
                datosFormaPago = requestData.get('datos_forma_pago', {})

                # Mapeo de claves del payload (requestData) a nombres de campos del modelo (solicitudData)
                solicitudData = {
                    # Campos JSON
                    'detalleDestinoFondos': detalleDestinoFondos,
                    'datos_forma_pago': datosFormaPago,

                    # Campos directos (CamelCase o snake_case que coinciden)
                    'lugarSolicitud': requestData.get('lugarSolicitud'),
                    'fechaSolicitud': requestData.get('fechaSolicitud'),
                    'fechaRealizacionActividad': requestData.get('fechaRealizacionActividad'),
                    'montoSolicitado': requestData.get('montoSolicitado'),
                    'validacionResponsable': requestData.get('validacionResponsable'),
                    'validacionCoordinador': requestData.get('validacionCoordinador'),
                    'descripcion_actividad': requestData.get('descripcion_actividad'),
                    'objetivo_actividad': requestData.get('objetivo_actividad'),

                    # IDs de Claves Foráneas (deben terminar en '_id')
                    'formaPago_id': requestData.get('formaPago_id'), 
                    'contador_id': requestData.get('contador_id'),
                    'coordinador_id': requestData.get('coordinador_id'),
                    'usuario_id': requestData.get('usuario_id'),
                    'actividad_id': requestData.get('actividad_id'),
                    'tarea_id': requestData.get('tarea_id'),
                    
                    # Campos con valor por defecto
                    'numeroFormulario': requestData.get('numeroFormulario'),
                    'bloquearIconosSolFondos': requestData.get('bloquearIconosSolFondos', True),
                }

                # NO filtrar campos opcionales (descripcion_actividad, objetivo_actividad, datos_forma_pago)
                # ya que el modelo los acepta como null=True y deben poder guardarse incluso si son None
                # Solo filtramos campos que realmente no pueden ser None (campos requeridos)
                # solicitudData = {k: v for k, v in solicitudData.items() if v is not None}  # COMENTADO
                
                # Se llama al caso de uso con los datos mapeados
                crearSolicitud = self.crearSolicitudFondosUseCase.execute(solicitudData)
                
                if crearSolicitud is not None:
                    return ReponseMapper.toSuccessResponse(crearSolicitud)
                else:
                    return ReponseMapper.toErrorResponse("Error al crear la solicitud de fondos")
            
            except json.JSONDecodeError:
                return ReponseMapper.toErrorResponse("Error en el formato JSON de detalle_destino_fondos o datos_forma_pago")
            except Exception as e:
                # Loguear el error y retornar una respuesta de error general
                print(f"Error al procesar solicitud: {e}") 
                return ReponseMapper.toErrorResponse(f"Error interno al crear la solicitud de fondos: {str(e)}")

    def obtenerSolicitudesFondos(self):
        solicitudes = self.crearSolicitudFondosUseCase.obtenerTodasLasSolicitudes()
        if solicitudes is not None:
            return ReponseMapper.toSolicitudesFondosResponse(solicitudes)
        else:
            return ReponseMapper.toErrorResponse("Error al obtener las solicitudes de fondos")
        
    def obtenerSolicitudesFondosPorFiltros(self, actividad_id, usuario_id, tarea_id=None):
        solicitudes = self.crearSolicitudFondosUseCase.obtenerSolicitudesPorFiltros(
            actividad_id=actividad_id,
            usuario_id=usuario_id,
            tarea_id=tarea_id
        )
        if solicitudes is not None:
            return ReponseMapper.toSolicitudesFondosResponse(solicitudes)
        else:
            return ReponseMapper.toErrorResponse("Error al obtener las solicitudes de fondos por filtros")
        
class RendicionCuentasPresenter:
    def __init__(self):
        self.useCaseContainer = CrearRendicionCuentasUseCaseContainer()
        self.crearRendicionCuentasUseCase = self.useCaseContainer.crearRendicionCuentasUseCase()

    def crearRendicionCuentas(self, requestData):
        crearRendicionCuentas = self.crearRendicionCuentasUseCase.execute(requestData)
        if crearRendicionCuentas is not None:
            return ReponseMapper.toSuccessResponse(crearRendicionCuentas)
        else:
            return ReponseMapper.toErrorResponse("Error al crear la rendicion de cuentas")
    
    def obtenerRendicionDeCuentas(self, filtros):
        rendiciones = self.crearRendicionCuentasUseCase.obtenerRendicionDeCuentas(filtros)
        if rendiciones is not None:
            return ReponseMapper.toRendicionesCuentasResponse(rendiciones)
        else:
            return ReponseMapper.toErrorResponse("Error al obtener las rendiciones de cuentas")
        
class SolicitudReembolsoPresenter:
    def __init__(self):
        self.useCaseContainer = CrearSolicitudReembolsoUseCaseContainer()
        self.crearSolicitudReembolsoUseCase = self.useCaseContainer.crearSolicitudReembolsoUseCase()

    # def crearSolicitudFondos(self, requestData):
    def crearSolicitudReembolso(self, requestData):
        crearSolicitud = self.crearSolicitudReembolsoUseCase.execute(requestData)
        if crearSolicitud is not None:
            return ReponseMapper.toSuccessResponse(crearSolicitud)
        else:
            return ReponseMapper.toErrorResponse("Error al crear la solicitud de Reembolso")
        
    def obtenerSolicitudReembolso(self, filtros):
        solicitudes = self.crearSolicitudReembolsoUseCase.obtenerSolicitudReembolso(filtros)
        if solicitudes is not None:
            return ReponseMapper.toSolicitudesReembolsoResponse(solicitudes)
        else:
            return ReponseMapper.toErrorResponse("Error al obtener las solicitudes de reembolso")

class SolicitudViajePresenter:
    def __init__(self):
        self.useCaseContainer = CrearSolicitudViajeUseCaseContainer()
        self.crearSolicitudViajeUseCase = self.useCaseContainer.crearSolicitudViajeUseCase()

    def crearSolicitudViaje(self, requestData):
        crearSolicitud = self.crearSolicitudViajeUseCase.execute(requestData)
        if crearSolicitud is not None:
            return ReponseMapper.toSuccessResponseSolicitudViaje(crearSolicitud)
        else:
            return ReponseMapper.toErrorResponse("Error al crear la solicitud de viaje")
        
    def obtenerSolicitudesViaje(self, filtros):
        solicitudes = self.crearSolicitudViajeUseCase.obtenerSolicitudesViaje(filtros)
        if solicitudes is not None:
            return ReponseMapper.toSolicitudesViajeResponse(solicitudes)
        else:
            return ReponseMapper.toErrorResponse("Error al obtener las solicitudes de viaje")

class SolicitudPagoDirectoPresenter:
    def __init__(self):
        self.useCaseContainer = CrearSolicitudPagoDirectoUseCaseContainer()
        self.crearSolicitudPagoDirectoUseCase = self.useCaseContainer.crearSolicitudPagoDirectoUseCase()

    def crearSolicitudPagoDirecto(self, requestData):
        crearSolicitud = self.crearSolicitudPagoDirectoUseCase.execute(requestData)
        if crearSolicitud is not None:
            return ReponseMapper.toSuccessResponse(crearSolicitud)
        else:
            return ReponseMapper.toErrorResponse("Error al crear la solicitud de Pago Directo")
        
    def obtenerSolicitudesPagoDirecto(self, filtros):
        solicitudes = self.crearSolicitudPagoDirectoUseCase.obtenerSolicitudesPagoDirecto(filtros)
        
        if solicitudes is not None:
            return ReponseMapper.toSolicitudesPagoDirectoResponse(solicitudes)
        else:
            return ReponseMapper.toErrorResponse("Error al obtener las solicitudes de pago directo")

class DatosFormularioPresenter:
    def __init__(self):
        self.useCaseContainer = ObtenerDatosFormularioUseCaseContainer()
        self.obtenerDatosFormularioUseCase = self.useCaseContainer.obtenerDatosFormularioUseCase()

    def obtenerDatosFormulario(self, requestData):

        obtenerDatos = self.obtenerDatosFormularioUseCase.execute(requestData)
        
        if obtenerDatos is not None:
            return obtenerDatos
        else:
            return ReponseMapper.toErrorResponse("Error al obtener los datos del formulario")
        
class ActualizarValidacionSolicitudFondosPresenter:
    def __init__(self):
        self.useCaseContainer = ActualizarValidacionSolicitudFondosUseCaseContainer()
        self.actualizarValidacionUseCase = self.useCaseContainer.actualizarValidacionSolicitudFondosUseCase()

    def actualizarValidacionSolicitudFondos(self, requestData):
        actualizarValidacion = self.actualizarValidacionUseCase.execute(requestData)
        if actualizarValidacion is not None:
            return actualizarValidacion
        else:
            return {"mensaje": "Error al actualizar la validación de la solicitud de fondos"}

class ActualizarValidacionRendicionCuentasPresenter:
    def __init__(self):
        self.useCaseContainer = ActualizarValidacionRendicionCuentasUseCaseContainer()
        self.actualizarValidacionUseCase = self.useCaseContainer.actualizarValidacionRendicionCuentasUseCase()

    def actualizarValidacionRendicionCuentas(self, requestData):
        actualizarValidacion = self.actualizarValidacionUseCase.execute(requestData)
        
        if actualizarValidacion is not None:
            return actualizarValidacion
        else:
            return {"mensaje": "Error al actualizar la validación de la rendición de cuentas"}
        
class ActualizarValidacionSolicitudReembolsoPresenter:
    def __init__(self):
        self.useCaseContainer = ActualizarValidacionSolicitudReembolsoUseCaseContainer()
        self.actualizarValidacionUseCase = self.useCaseContainer.actualizarValidacionSolicitudReembolsoUseCase()

    def actualizarValidacionSolicitudReembolso(self, requestData):
        actualizarValidacion = self.actualizarValidacionUseCase.execute(requestData)
        
        if actualizarValidacion is not None:
            return actualizarValidacion
        else:
            return {"mensaje": "Error al actualizar la validación de la solicitud de reembolso"}
        
class FormaPagoPresenter:
    def __init__(self):
        self.useCaseContainer = FormaPagoUseCaseContainer()
        self.formaPagoUseCase = self.useCaseContainer.formaPagoUseCase()

    def obtenerFormasPago(self, filtros):
        formasPago = self.formaPagoUseCase.obtenerFormasPago(filtros)
        
        if formasPago is not None:
            return ReponseMapper.toFormasPagoResponse(formasPago)
        else:
            return ReponseMapper.toErrorResponse("Error al obtener las formas de pago")
        
class ActualizarValidacionSolicitudViajePresenter:
    def __init__(self):
        self.useCaseContainer = ActualizarValidacionSolicitudViajeUseCaseContainer()
        self.actualizarValidacionUseCase = self.useCaseContainer.actualizarValidacionSolicitudViajeUseCase()

    def actualizarValidacionSolicitudViaje(self, requestData):
        actualizarValidacion = self.actualizarValidacionUseCase.execute(requestData)
        
        if actualizarValidacion is not None:
            return actualizarValidacion
        else:
            return {"mensaje": "Error al actualizar la validación de la solicitud de viaje"}
        
class ActualizarValidacionSolicitudPagoDirectoPresenter:
    def __init__(self):
        self.useCaseContainer = ActualizarValidacionSolicitudPagoDirectoUseCaseContainer()
        self.actualizarValidacionUseCase = self.useCaseContainer.actualizarValidacionSolicitudPagoDirectoUseCase()

    def actualizarValidacionSolicitudPagoDirecto(self, requestData):
        actualizarValidacion = self.actualizarValidacionUseCase.execute(requestData)
        
        if actualizarValidacion is not None:
            return actualizarValidacion
        else:
            return {"mensaje": "Error al actualizar la validación de la solicitud de pago directo"}
