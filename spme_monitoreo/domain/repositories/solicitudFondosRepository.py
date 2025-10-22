from spme_monitoreo.container.dataAccessContainer import SolicitudFondosDataAccessContainer

class SolicitudFondosRepository:
    def __init__(self):
        self.contenedor = SolicitudFondosDataAccessContainer()
        self.solicitudFondosDataAccess = self.contenedor.solicitudFondosDataAccess()

    def crearSolicitudFondos(self, solicitudData):
        """
        Crea una nueva solicitud de fondos en la base de datos.

        :param solicitud_data: Datos de la solicitud de fondos.
        :return: Resultado de la creación de la solicitud.
        """
        return self.solicitudFondosDataAccess.crearSolicitudFondos(solicitudData)
   
    # Nuevo método para obtener todas las solicitudes
    def obtenerTodasLasSolicitudes(self):
        """
        Obtiene todas las solicitudes de fondos de la base de datos.
        
        :return: Lista de todas las solicitudes de fondos.
        """
        return self.solicitudFondosDataAccess.obtenerSolicitudesFondos()
    
    def obtenerSolicitudesPorFiltros(self, actividad_id, usuario_id, tarea_id=None):
        """
        Obtiene solicitudes de fondos filtrando por actividad_id, usuario_id y tarea_id.
        
        :param actividad_id: ID de la actividad
        :param usuario_id: ID del usuario
        :param tarea_id: ID de la tarea (opcional)
        :return: Lista de solicitudes de fondos que coinciden con los filtros
        """
        return self.solicitudFondosDataAccess.obtenerSolicitudesPorFiltros(
            actividad_id=actividad_id,
            usuario_id=usuario_id,
            tarea_id=tarea_id
        )
    
    def actualizarValidacionSolicitudFondos(self, solicitudData):
        """
        Actualiza las validaciones de una solicitud de fondos existente.
        :param solicitud_data: Datos con las validaciones a actualizar.
        :return: Resultado de la actualización.
        """
        return self.solicitudFondosDataAccess.actualizarValidacionSolicitudFondos(solicitudData)
