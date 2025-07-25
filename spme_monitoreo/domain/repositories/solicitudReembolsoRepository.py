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
   
