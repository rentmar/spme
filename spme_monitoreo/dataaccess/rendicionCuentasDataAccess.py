from ..models import RendicionCuentas

class RendicionCuentasDataAccess:

    def crearRendicionCuentas(self, rendicionData):
        """
        Crea una nueva rendición de cuentas en la base de datos.

        :param rendicion_data: Datos de la rendición de cuentas.
        :return: Resultado de la creación de la rendición.
        """
        return RendicionCuentas.objects.create(**rendicionData)

    def obtenerRendicionesCuentas(self):
        """
        Obtiene todas las rendiciones de cuentas de la base de datos.

        :return: Lista de rendiciones de cuentas.
        """
        return RendicionCuentas.objects.all()