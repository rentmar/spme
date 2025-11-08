from spme_monitoreo.container.repositoryContainer import SolicitudViajeRepositoryContainer

class ActualizarValidacionSolicitudViajeUseCase:
    def __init__(self):
        self.contenedor = SolicitudViajeRepositoryContainer()
        self.solicitudViajeRepository = self.contenedor.solicitudViajeRepository()

    def execute(self, solicitudData):
        return self.solicitudViajeRepository.actualizarValidacionSolicitudViaje(solicitudData)