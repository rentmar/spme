from spme_estructuracion_pei.container.useCaseContainer import CrearEstructuraPeiUseCaseContainer
from spme_estructuracion_pei.mappers.estructuracionPeiMapper import EstructuracionPeiMapper

class EstructuracionPeiPresenter:
    def __init__(self):
        self.contenedor = CrearEstructuraPeiUseCaseContainer()
        self.crearEstructuraPeiUseCase = self.contenedor.crearEstructuraPeiUseCase()
        self.obtenerEstructuraPeiUseCase = self.contenedor.obtenerEstructuraPeiUseCaseContainer()
        
    def createEstructuraPei(self, request):
        """
        Crea un nuevo estructura pei a partir de la solicitud.
        """
        estructuraPei = self.crearEstructuraPeiUseCase.execute(request)
        if estructuraPei is not None:
            return EstructuracionPeiMapper.toSuccessResponse(estructuraPei)
        else:
            return None
        
    def obtenerEstructuraPei(self):
        estructuraPei = self.obtenerEstructuraPeiUseCase.execute()
        if estructuraPei is not None:
            return EstructuracionPeiMapper.toEstructuraPeiResponse(estructuraPei)
        else:
            return None