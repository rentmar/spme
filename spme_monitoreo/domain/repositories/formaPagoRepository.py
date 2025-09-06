from spme_monitoreo.container.dataAccessContainer import FormaPagoDataAccessContainer

class FormaPagoRepository:

     def __init__(self):
        self.contenedor = FormaPagoDataAccessContainer()
        self.formaPagoDataAccess = self.contenedor.formaPagoDataAccess()

    def obtenerFormaPagoPoId(self, idPago):
        """
        Obtiene forma de pago del id en la base de datos.

        :param id pago: Datos id forma de pago.
        :return: Resultado de obtener forma de pago.
        """
        return self.formaPagoDataAccess.obtenerFormaPagoPoId(idPago)