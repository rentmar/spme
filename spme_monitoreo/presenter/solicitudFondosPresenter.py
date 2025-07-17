from spme_monitoreo.container.useCaseContainer import CrearSolicitudFondosUseCaseContainer
from spme_monitoreo.mappers.monitoreoMapper import SolicitudFondosMapper

class SolicitudFondosPresenter:
    def __init__(self):
        self.useCaseContainer = CrearSolicitudFondosUseCaseContainer()
        self.crearSolicitudFondosUseCase = self.useCaseContainer.crearSolicitudFondosUseCase()
    def crearSolicitudFondos(self, requestData):
        # Lógica para crear la solicitud de fondos
        crearSolicitud = self.crearSolicitudFondosUseCase.execute(requestData)
        if crearSolicitud is not None:
            return SolicitudFondosMapper.toSuccessResponse(crearSolicitud)
        else:
            return SolicitudFondosMapper.toErrorResponse("Error al crear la solicitud de fondos")