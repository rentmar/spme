from container.objetivoEspecificoDataAccessContainer import ObjetivoEspecificoDataAccessContainer

class ObjetivoEspecificoRepository:
    def __init__(self):
        self.contenedor = ObjetivoEspecificoDataAccessContainer()
        self.objetivoEspecificoDataAccess = self.contenedor.objetivoEspecificoDataAccess()

    def objetivoEspecificoTodo(self):
        lista = self.objetivoEspecificoDataAccess.objetivoEspecificoTodo()
        return lista