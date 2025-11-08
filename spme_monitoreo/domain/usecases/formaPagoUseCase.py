from spme_monitoreo.container.repositoryContainer import FormaPagoRepositoryContainer

class FormaPagoUseCase:
    def __init__(self):
        self.contenedor = FormaPagoRepositoryContainer()
        self.formaPagoRepository = self.contenedor.formaPagoRepository()

    def obtenerFormasPago(self, filtros):
        """
        Obtiene formas de pago con filtros
        :param filtros: Diccionario con filtros
        :return: Lista de formas de pago
        """
        return self.formaPagoRepository.obtenerFormasPago(filtros)