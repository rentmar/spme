from spme_actividades.container.dataAccessContainer import ActividadesDataAccessContainer

class ActividadesRepository:
    def __init__(self):
        self.contenedor = ActividadesDataAccessContainer()
        self.actividadesDataAccess = self.contenedor.actividadesDataAccess()

    def obtenerActividadesPorUsuario(self, usuarioIdRequest):
        return self.actividadesDataAccess.obtenerActividadesPorUsuario(usuarioIdRequest['responsable_id'])

    def obtenerActividadesGanttId(self):
        return self.actividadesDataAccess.obtenerActividadesGanttId()

    def crearActividad(self,actividadRequest):
        return self.actividadesDataAccess.crearActividad(actividadRequest)
    
    def obtenerActividadPorId(self, actividadId):
        return self.actividadesDataAccess.obtenerActividadPorId(actividadId)
    
    def obtenerDatosFormActividadPorId(self, actividadId):
        return self.actividadesDataAccess.obtenerDatosFormActividadPorId(actividadId)

    def obtenerEncabezadoActividadPorId(self, encabezadoId):
        return self.actividadesDataAccess.obtenerEncabezadoActividadPorId(encabezadoId)

    def totalActividadesPlanificadas(self):
        return self.actividadesDataAccess.totalActividadesPlanificadas()
    
    def totalActividadesEnEjecucion(self):
        return self.actividadesDataAccess.totalActividadesEnEjecucion()

    def totalActividadesFinalizadas(self):
        return self.actividadesDataAccess.totalActividadesFinalizadas()

    def sumaPresupuestosGlobales(self):
        return self.actividadesDataAccess.sumaPresupuestosGlobales()
    
    def sumaPresupuestos(self):
        return self.actividadesDataAccess.sumaPresupuestos()