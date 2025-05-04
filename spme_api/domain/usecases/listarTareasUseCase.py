from ..repositories.tareasRepository import TareasRepositoy

class ListarTareasUseCase:
    def execute(self):
        tareasRespository = TareasRepositoy()
        return tareasRespository.getTareas()
    