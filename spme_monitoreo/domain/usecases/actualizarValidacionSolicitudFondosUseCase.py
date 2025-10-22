from spme_monitoreo.container.repositoryContainer import SolicitudFondosRepositoryContainer

class ActualizarValidacionSolicitudFondosUseCase:
    def __init__(self):
        self.contenedor = SolicitudFondosRepositoryContainer()
        self.solicitudFondosRepository = self.contenedor.solicitudFondosRepository()

    def execute(self, solicitudData):
        """
        Actualiza las validaciones de una solicitud de fondos.
        
        :param solicitud_data: Datos con las validaciones a actualizar.
        :return: Resultado de la actualización.
        """
        return self.solicitudFondosRepository.actualizarValidacionSolicitudFondos(solicitudData)