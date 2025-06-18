from container.objetivoEspecificoRepositoryContainer import ObjetivoEspecificoRepositoryContainer

class ObjetivoEspecificoUseCase:
    def __init__(self):
        self.contenedor = ObjetivoEspecificoRepositoryContainer()
        self.objetivoEspecificoRepository = self.contenedor.objetivoEspecificoRepository()

    def execute(self):
        lista = self.objetivoEspecificoRepository.objetivoEspecificoTodo()
        return lista
