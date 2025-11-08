from spme_monitoreo.container.repositoryContainer import SolicitudReembolsoRepositoryContainer

class ActualizarValidacionSolicitudReembolsoUseCase:
    def __init__(self):
        self.contenedor = SolicitudReembolsoRepositoryContainer()
        self.solicitudReembolsoRepository = self.contenedor.solicitudReembolsoRepository()

    def execute(self, solicitudData):
        """
        Actualiza las validaciones de una solicitud de reembolso.
        :param solicitud_data: Datos con las validaciones a actualizar.
        :return: Resultado de la actualización.
        """
        return self.solicitudReembolsoRepository.actualizarValidacionSolicitudReembolso(solicitudData)