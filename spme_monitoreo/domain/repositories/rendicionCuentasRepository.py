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

    def obtenerRendicionDeCuentas(self, filtros):
        """
        Obtiene rendiciones de cuentas con filtros
        :param filtros: Diccionario con filtros
        :return: Lista de rendiciones de cuentas
        """
        return self.rendicionCuentasDataAccess.obtenerRendicionDeCuentas(filtros)

    def actualizarValidacionRendicionCuentas(self, rendicionData):
        """
        Actualiza las validaciones de una rendición de cuentas existente.

        :param rendicion_data: Datos con las validaciones a actualizar.
        :return: Resultado de la actualización.
        """
        return self.rendicionCuentasDataAccess.actualizarValidacionRendicionCuentas(rendicionData)
