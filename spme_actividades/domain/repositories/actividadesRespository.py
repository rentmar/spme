from spme_actividades.container.dataAccessContainer import ActividadesDataAccessContainer

class ActividadesRepository:
    def __init__(self):
        self.contenedor = ActividadesDataAccessContainer()
        self.actividadesDataAccess = self.contenedor.actividadesDataAccess()

    def obtenerActividadesPorUsuario(self, usuarioIdRequest):
        return self.actividadesDataAccess.obtenerActividadesPorUsuario(usuarioIdRequest['user_id'])

    def obtenerActividadesPorKant(self):
        return self.actividadesDataAccess.obtenerActividadesPorKant()
    
    def crearActividad(self,actividadRequest):
        return self.actividadesDataAccess.crearActividad(actividadRequest)
    
    def obtenerActividadPorId(self, actividadId):
        return self.actividadesDataAccess.obtenerActividadPorId(actividadId)
    
    def obtenerDatosFormActividadPorId(self, actividadId):
        return self.actividadesDataAccess.obtenerDatosFormActividadPorId(actividadId)

    def obtenerEncabezadoActividadPorId(self, encabezadoId):
        return self.actividadesDataAccess.obtenerEncabezadoActividadPorId(encabezadoId)
    