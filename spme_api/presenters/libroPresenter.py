# from ..domain.usecases.getLibroUseCase import GetLibroUseCase
from ..domain.models.response.libroResponse import LibroResponse
from ..mappers.libroMapper import LibroMapper

from ..container.useCaseContainer import UseCaseContainer

class LibroPresenter:
    def __init__(self):
        self.contenedor =  UseCaseContainer()
        self.getLibroUseCase = self.contenedor.getLibroUseCase()
    
    def getLibro(self, validateData):
        #getLibroUseCase =  GetLibroUseCase()
        #libro = getLibroUseCase.execute(validateData)
        libro = self.getLibroUseCase.execute(validateData)
        return LibroMapper.toLibroResponse(libro)  
        