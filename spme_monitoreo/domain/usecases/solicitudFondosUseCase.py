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
    
        # Nuevo método para obtener todas las solicitudes
    def obtenerTodasLasSolicitudes(self):
        """
        Obtiene todas las solicitudes de fondos.
        
        :return: Lista de todas las solicitudes de fondos.
        """
        return self.solicitudFondosRepository.obtenerTodasLasSolicitudes()
    
    def obtenerSolicitudesPorFiltros(self, actividad_id, usuario_id, tarea_id=None):
        """
        Obtiene solicitudes de fondos filtrando por actividad_id, usuario_id y tarea_id.
        
        :param actividad_id: ID de la actividad
        :param usuario_id: ID del usuario
        :param tarea_id: ID de la tarea (opcional)
        :return: Lista de solicitudes de fondos que coinciden con los filtros
        """
        return self.solicitudFondosRepository.obtenerSolicitudesPorFiltros(
            actividad_id=actividad_id,
            usuario_id=usuario_id,
            tarea_id=tarea_id
        )