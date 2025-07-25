from spme_monitoreo.container.dataAccessContainer import RendicionCuentasDataAccessContainer

class RendicionCuentasRepository:
    def __init__(self):
        self.contenedor = RendicionCuentasDataAccessContainer()
        self.rendicionCuentasDataAccess = self.contenedor.rendicionCuentasDataAccess()

    def crearRendicionCuentas(self, rendicionData):
        """
        Crea una nueva rendición de cuentas en la base de datos.

        :param rendicion_data: Datos de la rendición de cuentas.
        :return: Resultado de la creación de la rendición.
        """
        return self.rendicionCuentasDataAccess.crearRendicionCuentas(rendicionData)

