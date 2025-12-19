from ..models import FormaPago
from django.core.exceptions import ObjectDoesNotExist

class FormaPagoDataAccess:
    
    def obtenerFormaPagoPorId(self,idPago):
        """
        Obtiene todas las solicitudes de viaje de la base de datos.

        :return: Lista de solicitudes de viaje.
        """
        try:
            return FormaPago.objects.get(id=idPago)
        except ObjectDoesNotExist:
            return None
        
    def obtenerFormasPago(self, filtros):
        """
        Obtiene formas de pago de la base de datos
        :param filtros: Diccionario con filtros
        :return: Lista de formas de pago
        """
        id_formaPago = filtros.get('id_formaPago')
        
        # Si se especifica un ID, buscar solo esa forma de pago
        if id_formaPago:
            try:
                formaPago = FormaPago.objects.get(id=id_formaPago)
                return [formaPago]
            except FormaPago.DoesNotExist:
                return []
        
        # Si no hay filtros, obtener todas las formas de pago
        return list(FormaPago.objects.all())