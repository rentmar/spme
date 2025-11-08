from spme_monitoreo.container.repositoryContainer import SolicitudPagoDirectoRepositoryContainer

class ActualizarValidacionSolicitudPagoDirectoUseCase:
    def __init__(self):
        self.contenedor = SolicitudPagoDirectoRepositoryContainer()
        self.solicitudPagoDirectoRepository = self.contenedor.solicitudPagoDirectoRepository()

    def execute(self, solicitudData):
        """
        Actualiza las validaciones de una solicitud de pago directo.
        :param solicitud_data: Datos con las validaciones a actualizar.
        :return: Resultado de la actualización.
        """
        return self.solicitudPagoDirectoRepository.actualizarValidacionSolicitudPagoDirecto(solicitudData)