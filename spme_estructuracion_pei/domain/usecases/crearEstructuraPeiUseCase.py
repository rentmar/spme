from spme_estructuracion_pei.container.repositoryContainer import EstructuracionPeiRepositoryContainer
    
class CrearEstructuraPeiUseCase:
    def __init__(self):
        self.contenedor = EstructuracionPeiRepositoryContainer() 
        self.estructuracionPeiRepository = self.contenedor.estructuracionPeiRepository()

    def execute(self, request):
        """Crea un nuevo structuracionPei a partir del request."""
        return self.estructuracionPeiRepository.createEstructuraPei(request)
    
class ObtenerEstructuraPeiUseCase:
    
    def __init__(self):
        self.contenedor = EstructuracionPeiRepositoryContainer() 
        self.estructuracionPeiRepository = self.contenedor.estructuracionPeiRepository()

    def execute(self):
        return self.estructuracionPeiRepository.obtenerEstructuraPei()

        
   