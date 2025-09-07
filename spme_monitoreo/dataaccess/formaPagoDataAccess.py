from ..models import FormaPago

class FormaPagoDataAccess:
    
    def obtenerFormaPagoPoId(self,idPago):
        """
        Obtiene todas las solicitudes de viaje de la base de datos.

        :return: Lista de solicitudes de viaje.
        """
        return FormaPago.objects.get(id=idPago)