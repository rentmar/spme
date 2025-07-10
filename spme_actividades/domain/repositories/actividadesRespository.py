from spme_actividades.container.dataAccessContainer import ActividadesDataAccessContainer

class ActividadesRepository:
    def __init__(self):
        self.contenedor = ActividadesDataAccessContainer()
        self.actividadesDataAccess = self.contenedor.actividadesDataAccess()

    def obtenerActividadesPorUsuario(self, usuarioIdRequest):
        return self.actividadesDataAccess.obtenerActividadesPorUsuario(usuarioIdRequest['user_id'])
