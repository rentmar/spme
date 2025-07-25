from ..models import SolicitudReembolso

class SolicitudReembolsoDataAccess:
    
    def crearSolicitudReembolso(self, solicitudData):
        """
        Crea una nueva solicitud de Reembolso en la base de datos.

        :param solicitud_data: Datos de la solicitud de Reembolso.
        :return: Resultado de la creación de la solicitud.
        """
        return SolicitudReembolso.objects.create(**solicitudData)

    def obtenerSolicitudesReembolso(self):
        """
        Obtiene todas las solicitudes de Reembolso de la base de datos.

        :return: Lista de solicitudes de Reembolso.
        """
        return SolicitudReembolso.objects.all()