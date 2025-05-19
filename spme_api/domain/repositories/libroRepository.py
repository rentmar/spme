from ...dataaccess.libroDataAccess import LibroDataAccess


class LibroRepository:
    def getLibro(self, validated_data):
        libroDataAccess = LibroDataAccess()
        libro = libroDataAccess.getLibro(validated_data['codigo'])
        return libro