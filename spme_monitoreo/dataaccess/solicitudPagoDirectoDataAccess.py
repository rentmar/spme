from ..models import SolicitudPagoDirecto

class SolicitudPagoDirectoDataAccess:

    def crearSolicitudPagoDirecto(self, solicitudData):
        """
        Crea una nueva solicitud de pago directo en la base de datos.

        :param solicitud_data: Datos de la solicitud de pago directo.
        :return: Resultado de la creación de la solicitud.
        """
        return SolicitudPagoDirecto.objects.create(**solicitudData)

    def obtenerSolicitudesPagoDirecto(self):
        """
        Obtiene todas las solicitudes de pago directo de la base de datos.

        :return: Lista de solicitudes de pago directo.
        """
        return SolicitudPagoDirecto.objects.all()