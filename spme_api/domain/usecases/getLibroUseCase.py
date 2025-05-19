from ..repositories.libroRepository import LibroRepository

class GetLibroUseCase:
    def execute(self, validate_data):
        libroRepositorio = LibroRepository()
        libro = libroRepositorio.getLibro(validate_data)
        return libro