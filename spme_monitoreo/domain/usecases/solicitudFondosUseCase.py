from spme_monitoreo.container.repositoryContainer import SolicitudFondosRepositoryContainer

class CrearSolicitudFondosUseCase:
    def __init__(self):
        self.contenedor = SolicitudFondosRepositoryContainer()
        self.solicitudFondosRepository = self.contenedor.solicitudFondosRepository()

    def execute(self, solicitudData):
        """
        Crea una nueva solicitud de fondos.
        
        :param solicitud_data: Datos de la solicitud de fondos.
        :return: Resultado de la creación de la solicitud.
        """
        return self.solicitudFondosRepository.crearSolicitudFondos(solicitudData)

