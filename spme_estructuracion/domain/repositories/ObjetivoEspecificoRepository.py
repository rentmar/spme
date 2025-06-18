from ...dataaccess.ObjetivoEspecificoDataAccess import ObjetivoEspecificoDataAccess

class ObjetivoEspecificoRepository:
    def objetivoEspecificoTodo(self):
        objetivoEspecificoDataAccess = ObjetivoEspecificoDataAccess()
        objetivoEspecifico = objetivoEspecificoDataAccess.objetivoEspecificoTodo()
        return objetivoEspecifico