from ..models import SolicitudViaje

class SolicitudViajeDataAccess:

    def crearSolicitudViaje(self, solicitudData):
        """
        Crea una nueva solicitud de viaje en la base de datos.

        :param solicitud_data: Datos de la solicitud de viaje.
        :return: Resultado de la creación de la solicitud.
        """
        return SolicitudViaje.objects.create(**solicitudData)

    def obtenerSolicitudesViaje(self):
        """
        Obtiene todas las solicitudes de viaje de la base de datos.

        :return: Lista de solicitudes de viaje.
        """
        return SolicitudViaje.objects.all()