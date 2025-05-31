from ...dataaccess.libroDataAccess import LibroDataAccess
#from ...container.libroContainer import LibroContainer


class LibroRepository:
    # def __init__(self):
    #     self.cont = LibroContainer()
    #     self.libroDataAccess = self.cont.libroDataAccess()
    
    def getLibro(self, validated_data):
        libroDataAccess = LibroDataAccess()
        libro = libroDataAccess.getLibro(validated_data['codigo'])
        return libro