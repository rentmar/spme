from spme_monitoreo.container.repositoryContainer import RendicionCuentasRepositoryContainer

class CrearRendicionCuentasUseCase:
    def __init__(self):
        self.contenedor = RendicionCuentasRepositoryContainer()
        self.rendicionCuentasRepository = self.contenedor.rendicionCuentasRepository()

    def execute(self, rendicionData):
        """
        Crea una nueva rendición de cuentas.

        :param rendicion_data: Datos de la rendición de cuentas.
        :return: Resultado de la creación de la rendición.
        """
        return self.rendicionCuentasRepository.crearRendicionCuentas(rendicionData)
    
    def obtenerRendicionDeCuentas(self, filtros):
        """
        Obtiene rendiciones de cuentas con filtros
        :param filtros: Diccionario con filtros (id_actividad, id_tarea, usuario)
        :return: Lista de rendiciones de cuentas
        """
        return self.rendicionCuentasRepository.obtenerRendicionDeCuentas(filtros)