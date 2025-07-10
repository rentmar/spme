from spme_actividades.container.useCaseContainer import ActividadesUseCaseContainer
from spme_actividades.mappers.actividadesMapper import ActividadesMapper

class ActividadesPresenter:
    def __init__(self):
        self.useCaseContainer = ActividadesUseCaseContainer()
        self.obtenerActividadesUsuarioUseCase = self.useCaseContainer.obtenerActividadesUsuarioUseCase()

    def obtenerActividadesUsuario(self, userIdRequest):
        actividadesList = self.obtenerActividadesUsuarioUseCase.execute(userIdRequest)
        if actividadesList is not None:
            return ActividadesMapper.toActividadesUsuarioResponse(actividadesList)
        else:
            return []