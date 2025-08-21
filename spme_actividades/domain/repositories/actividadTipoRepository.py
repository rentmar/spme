from spme_actividades.container.dataAccessContainer import TipoActividadDataAccessContainer

class ActividadTipoRepository:
    def __init__(self):
        self.contenedor = TipoActividadDataAccessContainer()
        self.tipoActividadDataAccess = self.contenedor.tipoActividadDataAccess()

    def obtenerTipoActividadPorId(self, tipoId):
        return self.tipoActividadDataAccess.obtenerTipoActividadPorId(tipoId)