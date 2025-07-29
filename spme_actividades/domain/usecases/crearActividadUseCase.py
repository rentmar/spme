from spme_actividades.container.repositoryContainer import ActividadesRepositoryContainer

class CrearActividadUseCase:
    def __init__(self):
        self.contenedor = ActividadesRepositoryContainer()
        self.actividadesRepository = self.contenedor.actividadesRepository()

    def execute(self, actividadRequest):
       
        return self.actividadesRepository.crearActividad(actividadRequest)
