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

    def crearSolicitudFondos(self, requestData):
        crearSolicitud = self.crearSolicitudFondosUseCase.execute(requestData)
        if crearSolicitud is not None:
            return ReponseMapper.toSuccessResponse(crearSolicitud)
        else:
            return ReponseMapper.toErrorResponse("Error al crear la solicitud de fondos")
    
        # Nuevo método para obtener todas las solicitudes
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
