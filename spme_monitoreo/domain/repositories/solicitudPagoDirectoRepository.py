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
   
