from ..domain.usecases.getLibroUseCase import GetLibroUseCase
from ..domain.models.response.libroResponse import LibroResponse
from ..mappers.libroMapper import LibroMapper

class LibroPresenter:
    def getLibro(self, validateData):
        getLibroUseCase = GetLibroUseCase()
        libro = getLibroUseCase.execute(validateData)
        return LibroMapper.toLibroResponse(libro)  
        