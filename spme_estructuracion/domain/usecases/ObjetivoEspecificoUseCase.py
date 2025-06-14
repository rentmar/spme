from ..repositories.ObjetivoEspecificoRepository import ObjetivoEspecificoRepository


class ObjetivoEspecificoUseCase:
    def execute(self):
        objetivoEspecificoRepositorio = ObjetivoEspecificoRepository()
        lista = objetivoEspecificoRepositorio.objetivoEspecificoTodo()
        return lista
