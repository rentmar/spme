from spme_monitoreo.container.useCaseContainer import CrearSolicitudFondosUseCaseContainer,CrearRendicionCuentasUseCaseContainer,CrearSolicitudReembolsoUseCaseContainer
from spme_monitoreo.mappers.monitoreoMapper import ReponseMapper

class SolicitudFondosPresenter:
    def __init__(self):
        #Capa Inferior, inyeccion de datos
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