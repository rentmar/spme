from spme_monitoreo.container.repositoryContainer import SolicitudViajeRepositoryContainer,FormaPagoRepositoryContainer
from spme_autenticacion.container.repositoryContainer import UserRepositoryContainer

class CrearSolicitudViajeUseCase:
    
    def __init__(self):
        self.contenedor = SolicitudViajeRepositoryContainer()
        self.solicitudViajeRepository = self.contenedor.solicitudViajeRepository()
        self.contenedorFormaPago = FormaPagoRepositoryContainer()
        self.formaPagoRepository = self.contenedorFormaPago.formaPagoRepository()
        self.contenedorUser = UserRepositoryContainer()
        self.userRepository = self.contenedorUser.userRepository()

    def execute(self, requestData):
        """
        Crea una nueva solicitud de viaje.

        :param solicitud_data: Datos de la solicitud de viaje.
        :return: Resultado de la creación de la solicitud.
        """
        formaPago = self.formaPagoRepositoty(requestData["formaPago"])
        responsable = self.userRepository.obtenerNombreUsuarioPorId(requestData["idResponsable"])
        coordinador = self.userRepository.obtenerNombreUsuarioPorId(requestData["idCoordinador"])
        usuario = self.userRepository.obtenerNombreUsuarioPorId(requestData["idUsuario"])

        solicitud_data = {
                **requestData,
                "formaPago": formaPago,
                "idResponsable": responsable,
                "idCoordinador": coordinador,
                "idUsuario": usuario
            }

        return self.solicitudViajeRepository.crearSolicitudViaje(solicitud_data)

