from spme_estructuracion.container.objetivoEspecificoUseCaseContainer import ObjetivoEspecificoUseCaseContainer
from ..mappers.ObjetivoEspecificoMapper import ObjetivoEspecificoMapper

class ObjetivoEspecificoPresenter:
    def __init__(self):
        self.contenedor = ObjetivoEspecificoUseCaseContainer()
        self.objetivoEspecificoRepository = self.contenedor.objetivoEspecificoUseCase()

    def ObjetivoEspecifico(self):
       
        lista = self.objetivoEspecificoRepository.execute()

        return ObjetivoEspecificoMapper.toObjetivoEspecificoResponse(lista)