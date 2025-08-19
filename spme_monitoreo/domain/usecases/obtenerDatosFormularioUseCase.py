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
       
        validadores = list(self.userRepository.obtenerListaValidadores())
        #actividadData = self.actividadesRepository.obtenerDatosFormActividadPorId(requestData["id"])
        formaPago =[
            "Transferencia","Deposito","Cheque","QR"
        ]
        actividadData = {
            "id":1,
            "descripcion": "Actividad de prueba",
            "fecha_inicio": "2025-08-01",
            "fecha_fin": "2025-08-10",
            "objetivo_de_actividad": "Objetivo de la actividad de prueba"
        }

        return {"usuario": userData,"actividad": actividadData,"validadores": validadores, "formaPago": formaPago}