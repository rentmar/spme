from spme_monitoreo.container.useCaseContainer import CrearSolicitudFondosUseCaseContainer,CrearRendicionCuentasUseCaseContainer,CrearSolicitudReembolsoUseCaseContainer,CrearSolicitudViajeUseCaseContainer,CrearSolicitudPagoDirectoUseCaseContainer,ObtenerDatosFormularioUseCaseContainer
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
        
class SolicitudReembolsoPresenter:
    def __init__(self):
        self.useCaseContainer = CrearSolicitudReembolsoUseCaseContainer()
        self.crearSolicitudReembolsoUseCase = self.useCaseContainer.crearSolicitudReembolsoUseCase()

    def crearSolicitudFondos(self, requestData):
        crearSolicitud = self.crearSolicitudReembolsoUseCase.execute(requestData)
        if crearSolicitud is not None:
            return ReponseMapper.toSuccessResponse(crearSolicitud)
        else:
            return ReponseMapper.toErrorResponse("Error al crear la solicitud de Reembolso")

class SolicitudViajePresenter:
    def __init__(self):
        self.useCaseContainer = CrearSolicitudViajeUseCaseContainer()
        self.crearSolicitudViajeUseCase = self.useCaseContainer.crearSolicitudViajeUseCase()

    def crearSolicitudViaje(self, requestData):
        crearSolicitud = self.crearSolicitudViajeUseCase.execute(requestData)
        if crearSolicitud is not None:
            return ReponseMapper.toSuccessResponse(crearSolicitud)
        else:
            return ReponseMapper.toErrorResponse("Error al crear la solicitud de Viaje")

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