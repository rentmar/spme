from spme_monitoreo.container.dataAccessContainer import SolicitudPagoDirectoDataAccessContainer

class SolicitudPagoDirectoRepository:
    def __init__(self):
        self.contenedor = SolicitudPagoDirectoDataAccessContainer()
        self.solicitudPagoDirectoDataAccess = self.contenedor.solicitudPagoDirectoDataAccess()

    def crearSolicitudPagoDirecto(self, solicitudData):
        """
        Crea una nueva solicitud de pago directo en la base de datos.

        :param solicitud_data: Datos de la solicitud de pago directo.
        :return: Resultado de la creación de la solicitud.
        """
        return self.solicitudPagoDirectoDataAccess.crearSolicitudPagoDirecto(solicitudData)
   
    def obtenerSolicitudesPagoDirecto(self, filtros):
        """
        Obtiene solicitudes de pago directo con filtros
        :param filtros: Diccionario con filtros
        :return: Lista de solicitudes de pago directo
        """
        return self.solicitudPagoDirectoDataAccess.obtenerSolicitudesPagoDirecto(filtros)
    
    def actualizarValidacionSolicitudPagoDirecto(self, solicitudData):
        """
        Actualiza las validaciones de una solicitud de pago directo existente.
        :param solicitud_data: Datos con las validaciones a actualizar.
        :return: Resultado de la actualización.
        """
        return self.solicitudPagoDirectoDataAccess.actualizarValidacionSolicitudPagoDirecto(solicitudData)