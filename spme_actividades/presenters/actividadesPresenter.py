from spme_actividades.container.useCaseContainer import ActividadesUseCaseContainer
from spme_actividades.mappers.actividadesMapper import ActividadesMapper

class ActividadesPresenter:
    def __init__(self):
        self.useCaseContainer = ActividadesUseCaseContainer()
        self.obtenerActividadesUsuarioUseCase = self.useCaseContainer.obtenerActividadesUsuarioUseCase()
        self.obtenerActividadesKantUseCase = self.useCaseContainer.obtenerActividadesKantUseCase()
        self.crearActividadUseCase = self.useCaseContainer.crearActividadUseCase()

    def obtenerActividadesUsuario(self, userIdRequest):
        actividadesList = self.obtenerActividadesUsuarioUseCase.execute(userIdRequest)
        if actividadesList is not None:
            return ActividadesMapper.toActividadesUsuarioResponse(actividadesList)
        else:
            return []

    def obtenerActividadesKant(self):
        actividadesList = self.obtenerActividadesKantUseCase.execute()
       
        if actividadesList is not None:
            return ActividadesMapper.toActividadesKantResponse(actividadesList)
        else:
            return []
        
    def crearActividad(self,actividadRequest):
        crearActividadRespose = self.crearActividadUseCase.execute(actividadRequest)
        if crearActividadRespose is not None:
            return ActividadesMapper.toSuccessResponse(crearActividadRespose)
        else:
            return ActividadesMapper.toErrorResponse("Error al crear la solicitud de Reembolso")