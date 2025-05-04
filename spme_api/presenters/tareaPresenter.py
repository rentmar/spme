from ..domain.usecases.listarTareasUseCase import ListarTareasUseCase

class TareaPresenter:
    def getTareas(self):
        lista = ListarTareasUseCase()
        return lista.execute()