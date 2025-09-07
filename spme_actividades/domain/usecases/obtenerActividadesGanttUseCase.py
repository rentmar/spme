from spme_actividades.container.repositoryContainer import ActividadesRepositoryContainer

class ObtenerActividadesGanttUseCase:
    def __init__(self):
        self.contenedor = ActividadesRepositoryContainer()
        self.actividadesRepository = self.contenedor.actividadesRepository()

    def execute(self,request):
        return self.actividadesRepository.obtenerActividadesGanttId(request['responsable_id'])