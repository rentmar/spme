from spme_actividades.container.repositoryContainer import ActividadesRepositoryContainer

class ObtenerActividadesUsuarioUseCase:
    def __init__(self):
        self.contenedor = ActividadesRepositoryContainer()
        self.actividadesRepository = self.contenedor.actividadesRepository()

    def execute(self, usuarioIdRequest):
        # Aquí se llamaría al método del presenter para obtener las actividades del usuario
        return self.actividadesRepository.obtenerActividadesPorUsuario(usuarioIdRequest)