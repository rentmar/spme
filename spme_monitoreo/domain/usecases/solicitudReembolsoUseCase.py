from spme_monitoreo.container.repositoryContainer import SolicitudReembolsoRepositoryContainer

class CrearSolicitudReembolsoUseCase:
    def __init__(self):
        self.contenedor = SolicitudReembolsoRepositoryContainer()
        self.solicitudReembolsoRepository = self.contenedor.solicitudReembolsoRepository()

    def execute(self, solicitudData):
        """
        Crea una nueva solicitud de Reembolso.
        
        :param solicitud_data: Datos de la solicitud de Reembolso.
        :return: Resultado de la creación de la solicitud.
        """
        return self.solicitudReembolsoRepository.crearSolicitudReembolso(solicitudData)

