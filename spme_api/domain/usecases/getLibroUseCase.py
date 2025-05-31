from ..repositories.libroRepository import LibroRepository
#from ...container.libroContainer import LibroContainer

class GetLibroUseCase:
    # def __init__(self):
    #     self.cont = LibroContainer()
    #     self.libroRepositorio = self.cont.libroRepository
    def execute(self, validate_data):
        libroRepositorio = LibroRepository()
        libro = libroRepositorio.getLibro(validate_data)
        return libro