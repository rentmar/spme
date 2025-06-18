from ..domain.usecases.ObjetivoEspecificoUseCase import ObjetivoEspecificoUseCase
from ..mappers.ObjetivoEspecificoMapper import ObjetivoEspecificoMapper

class ObjetivoEspecificoPresenter:
    def ObjetivoEspecifico(self):
        #objetivoEspecificoUseCase = ObjetivoEspecificoUseCase()  #no instanciar clase USAR DI        
        lista = objetivoEspecificoUseCase.execute()

        return ObjetivoEspecificoMapper.toObjetivoEspecificoResponse(lista)