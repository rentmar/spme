from ..models import SolicitudFondos

class SolicitudFondosDataAccess:
    
    def crearSolicitudFondos(self, solicitudData):
        """
        Crea una nueva solicitud de fondos en la base de datos.

        :param solicitud_data: Datos de la solicitud de fondos.
        :return: Resultado de la creación de la solicitud.
        """
        return SolicitudFondos.objects.create(**solicitudData)

    def obtenerSolicitudesFondos(self):
        """
        Obtiene todas las solicitudes de fondos de la base de datos.

        :return: Lista de solicitudes de fondos.
        """
        return SolicitudFondos.objects.all()