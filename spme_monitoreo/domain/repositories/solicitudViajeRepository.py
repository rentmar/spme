from spme_monitoreo.container.dataAccessContainer import SolicitudViajeDataAccessContainer

class SolicitudViajeRepository:
    def __init__(self):
        self.contenedor = SolicitudViajeDataAccessContainer()
        self.solicitudViajeDataAccess = self.contenedor.solicitudViajeDataAccess()

    def crearSolicitudViaje(self, solicitudData):
        """
        Crea una nueva solicitud de viaje en la base de datos.

        :param solicitud_data: Datos de la solicitud de viaje.
        :return: Resultado de la creación de la solicitud.
        """
        return self.solicitudViajeDataAccess.crearSolicitudViaje(solicitudData)
   
