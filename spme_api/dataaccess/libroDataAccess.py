from ..models import Libro

class LibroDataAccess:
    #Instancia Libro
    def getLibro(self, codigo):
        libro = Libro.objects.get(codigo=codigo)
        return libro

        

