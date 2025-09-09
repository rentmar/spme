from spme_monitoreo.container.repositoryContainer import SolicitudViajeRepositoryContainer,FormaPagoRepositoryContainer
from spme_autenticacion.container.repositoryContainer import UserRepositoryContainer
from spme_actividades.container.repositoryContainer import ActividadesRepositoryContainer

class CrearSolicitudViajeUseCase:
    
    def __init__(self):
        self.contenedor = SolicitudViajeRepositoryContainer()
        self.solicitudViajeRepository = self.contenedor.solicitudViajeRepository()
        self.contenedorFormaPago = FormaPagoRepositoryContainer()
        self.formaPagoRepository = self.contenedorFormaPago.formaPagoRepository()
        self.contenedorUser = UserRepositoryContainer()
        self.userRepository = self.contenedorUser.userRepository()
        self.contenedorActividad = ActividadesRepositoryContainer()
        self.actividadesRepository = self.contenedorActividad.actividadesRepository()

    def execute(self, requestData):
        """
        Crea una nueva solicitud de viaje.

        :param solicitud_data: Datos de la solicitud de viaje.
        :return: Resultado de la creación de la solicitud.
        """
        return self.solicitudViajeRepository.crearSolicitudViaje(requestData)
        