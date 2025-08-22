from spme_autenticacion.container.repositoryContainer import UserRepositoryContainer
from spme_actividades.container.repositoryContainer import ActividadesRepositoryContainer

class ObtenerDatosFormularioUseCase:
    def __init__(self):
        self.userContainer = UserRepositoryContainer()
        self.actividadesContainer = ActividadesRepositoryContainer()
        self.userRepository = self.userContainer.userRepository()
        self.actividadesRepository = self.actividadesContainer.actividadesRepository()

    def execute(self, requestData):
        userData = self.userRepository.obtenerUsuarioPorUsername(requestData["username"])
        
        if not userData:
            return None
        validadores = list(self.userRepository.obtenerListaValidadores())
        if not validadores:
            return None
        actividadData = self.actividadesRepository.obtenerDatosFormActividadPorId(requestData["id"])
        if not actividadData:
            return None
        formaPago =[
            "Transferencia","Deposito","Cheque","QR"
        ]

        return {"usuario": userData,"actividad": actividadData,"validadores": validadores, "formaPago": formaPago}