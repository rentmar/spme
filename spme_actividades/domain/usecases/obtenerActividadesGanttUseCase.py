from spme_actividades.container.repositoryContainer import ActividadesRepositoryContainer
from spme_autenticacion.container.repositoryContainer import UserRepositoryContainer
class ObtenerActividadesGanttUseCase:
    def __init__(self):
        self.contenedor = ActividadesRepositoryContainer()
        self.actividadesRepository = self.contenedor.actividadesRepository()
        self.userRepositoryContainer = UserRepositoryContainer()
        self.userRepository = self.userRepositoryContainer.userRepository()

    def execute(self):

        actividades = self.actividadesRepository.obtenerActividadesGanttId()

        if actividades: 
            for actividad in actividades:
                responsable_id = actividad.get("responsable_id")
                if responsable_id:
                    nombre_responsable = self.userRepository.obtenerNombreUsuarioPorId(responsable_id)
                    if nombre_responsable:
                        actividad['nombre_responsable'] = (
                            nombre_responsable["nombre"] + " " +
                            nombre_responsable["paterno"] + " " +
                            nombre_responsable["materno"]
                        )
                    else:
                        actividad['nombre_responsable'] = "Responsable no encontrado"
            return actividades 
        else:
            return None
