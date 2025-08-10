from spme_monitoreo.container.repositoryContainer import SolicitudViajeRepositoryContainer

class CrearSolicitudViajeUseCase:
    def __init__(self):
        self.contenedor = SolicitudViajeRepositoryContainer()
        self.solicitudViajeRepository = self.contenedor.solicitudViajeRepository()

    def execute(self, solicitudData):
        """
        Crea una nueva solicitud de viaje.

        :param solicitud_data: Datos de la solicitud de viaje.
        :return: Resultado de la creación de la solicitud.
        """
        return self.solicitudViajeRepository.crearSolicitudViaje(solicitudData)

