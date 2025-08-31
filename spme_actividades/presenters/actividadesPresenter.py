from spme_actividades.container.useCaseContainer import ActividadesUseCaseContainer
from spme_actividades.mappers.actividadesMapper import ActividadesMapper

class ActividadesPresenter:
    def __init__(self):
        self.useCaseContainer = ActividadesUseCaseContainer()
        self.obtenerActividadesUsuarioUseCase = self.useCaseContainer.obtenerActividadesUsuarioUseCase()
        self.obtenerActividadesGantUseCase = self.useCaseContainer.obtenerActividadesGantUseCase()
        self.crearActividadUseCase = self.useCaseContainer.crearActividadUseCase()
        self.obtenerActividadPorIdUseCase = self.useCaseContainer.obtenerActividadPorIdUseCase()
        self.obtenerEncabezadoActividadPorIdUseCase = self.useCaseContainer.obtenerEncabezadoActividadPorIdUseCase()

    def obtenerActividadesUsuario(self, userIdRequest):
        actividadesList = self.obtenerActividadesUsuarioUseCase.execute(userIdRequest)
        if actividadesList is not None:
            return ActividadesMapper.toActividadesUsuarioResponse(actividadesList)
        else:
            return []

    def obtenerActividadesGant(self,request):
        actividadesList = self.obtenerActividadesGantUseCase.execute(request)
       
        if actividadesList is not None:
            return ActividadesMapper.toActividadesGantResponse(actividadesList)
        else:
            return []
        
    def crearActividad(self,actividadRequest):
        crearActividadRespose = self.crearActividadUseCase.execute(actividadRequest)
        if crearActividadRespose is not None:
            return ActividadesMapper.toSuccessResponse(crearActividadRespose)
        else:
            return ActividadesMapper.toErrorResponse("Error al crear la solicitud de Reembolso")
        
    def obtenerActividadPorId(self, actividadIdRequest):
        actividad = self.obtenerActividadPorIdUseCase.execute(actividadIdRequest)
        if actividad is not None:
            return ActividadesMapper.toObtenerActividadIdResponse(actividad)
        else:
            return ActividadesMapper.toErrorResponse("Actividad no encontrada")
        
    def obtenerEncabezadoActividadPorId(self, encabezadoIdRequest):
        encabezado = self.obtenerEncabezadoActividadPorIdUseCase.execute(encabezadoIdRequest)
        if encabezado is not None:
            return ActividadesMapper.toObtenerEncabezadoActividadResponse(encabezado)
        else:
            return ActividadesMapper.toErrorResponse("Encabezado de actividad no encontrado")
