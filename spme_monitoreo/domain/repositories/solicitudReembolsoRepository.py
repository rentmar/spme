from spme_monitoreo.container.dataAccessContainer import SolicitudReembolsoDataAccessContainer

class SolicitudReembolsoRepository:
    def __init__(self):
        self.contenedor = SolicitudReembolsoDataAccessContainer()
        self.solicitudReembolsoDataAccess = self.contenedor.solicitudReembolsoDataAccess()

    def crearSolicitudReembolso(self, solicitudData):
        """
        Crea una nueva solicitud de Reembolso en la base de datos.

        :param solicitud_data: Datos de la solicitud de Reembolso.
        :return: Resultado de la creación de la solicitud.
        """
        return self.solicitudReembolsoDataAccess.crearSolicitudReembolso(solicitudData)
   
    def obtenerSolicitudReembolso(self, filtros):
        """
        Obtiene solicitudes de reembolso con filtros
        :param filtros: Diccionario con filtros
        :return: Lista de solicitudes de reembolso
        """
        return self.solicitudReembolsoDataAccess.obtenerSolicitudReembolso(filtros)
    
    def actualizarValidacionSolicitudReembolso(self, solicitudData):
        """
        Actualiza las validaciones de una solicitud de reembolso existente.
        :param solicitud_data: Datos con las validaciones a actualizar.
        :return: Resultado de la actualización.
        """
        return self.solicitudReembolsoDataAccess.actualizarValidacionSolicitudReembolso(solicitudData)