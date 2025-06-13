from ..repositories.peiRepository import PeiRepository

class ObtenerListaPeiUseCase:
    def execute(self):
        peiRepositorio = PeiRepository()
        qsPei = peiRepositorio.getListaPei()
        return qsPei