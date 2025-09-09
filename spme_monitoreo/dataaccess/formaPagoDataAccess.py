from ..models import FormaPago
from django.core.exceptions import ObjectDoesNotExist

class FormaPagoDataAccess:
    
    def obtenerFormaPagoPoId(self,idPago):
        """
        Obtiene todas las solicitudes de viaje de la base de datos.

        :return: Lista de solicitudes de viaje.
        """
        try:
            return FormaPago.objects.get(id=idPago)
        except ObjectDoesNotExist:
            return None