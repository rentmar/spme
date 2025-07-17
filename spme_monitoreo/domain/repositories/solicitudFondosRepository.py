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
   
