from spme_actividades.container.repositoryContainer import ActividadesRepositoryContainer

class ObtenerActividadPorIdUseCase:
    def __init__(self):
        self.contenedor = ActividadesRepositoryContainer()
        self.actividadesRepository = self.contenedor.actividadesRepository()

    def execute(self, actividadIdRequest):
        return self.actividadesRepository.obtenerActividadPorId(actividadIdRequest['actividad_id'])