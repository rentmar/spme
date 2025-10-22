from spme_monitoreo.container.repositoryContainer import RendicionCuentasRepositoryContainer

class ActualizarValidacionRendicionCuentasUseCase:
    def __init__(self):
        self.contenedor = RendicionCuentasRepositoryContainer()
        self.rendicionCuentasRepository = self.contenedor.rendicionCuentasRepository()

    def execute(self, rendicionData):
        """
        Actualiza las validaciones de una rendición de cuentas.

        :param rendicion_data: Datos con las validaciones a actualizar.
        :return: Resultado de la actualización.
        """
        return self.rendicionCuentasRepository.actualizarValidacionRendicionCuentas(rendicionData)