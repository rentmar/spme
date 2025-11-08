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

    def obtenerSolicitudesPagoDirecto(self, filtros):
        """
        Obtiene solicitudes de pago directo con filtros
        :param filtros: Diccionario con filtros (id_solicitudPagoDirecto, id_actividad, id_tarea, usuario)
        :return: Lista de solicitudes de pago directo
        """
        return self.solicitudPagoDirectoRepository.obtenerSolicitudesPagoDirecto(filtros)