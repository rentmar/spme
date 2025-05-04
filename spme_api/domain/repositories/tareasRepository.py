from ...dataaccess.tareasDataAccess import TareasDataAccess 

class TareasRepositoy:

    def getTareas(self):
        tareasDataAccess = TareasDataAccess()
        return tareasDataAccess.getTareas()