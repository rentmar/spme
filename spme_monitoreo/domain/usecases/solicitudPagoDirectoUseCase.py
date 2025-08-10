from spme_monitoreo.container.repositoryContainer import SolicitudPagoDirectoRepositoryContainer

class CrearSolicitudPagoDirectoUseCase:
    def __init__(self):
        self.contenedor = SolicitudPagoDirectoRepositoryContainer()
        self.solicitudPagoDirectoRepository = self.contenedor.solicitudPagoDirectoRepository()

    def execute(self, solicitudData):
        """
        Crea una nueva solicitud de pago directo.

        :param solicitud_data: Datos de la solicitud de pago directo.
        :return: Resultado de la creación de la solicitud.
        """
        return self.solicitudPagoDirectoRepository.crearSolicitudPagoDirecto(solicitudData)

