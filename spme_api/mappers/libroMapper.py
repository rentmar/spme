
class LibroMapper:
    @staticmethod
    def toLibroResponse(libro):
        libroResponse = {
            'titulo':libro.titulo,
            'disponible': libro.disponible
        }
        return libroResponse