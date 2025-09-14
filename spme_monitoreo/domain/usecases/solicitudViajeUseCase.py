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
        # actividad = self.actividadesRepository.obtenerActividadPorId(requestData["actividad_id"])
        # formaPago = self.formaPagoRepository.obtenerFormaPagoPoId(requestData["formaPago_id"])
        # responsable = self.userRepository.obtenerNombreUsuarioPorId(requestData["responsable_id"])
        # coordinador = self.userRepository.obtenerNombreUsuarioPorId(requestData["coordinador_id"])
        # usuario = self.userRepository.obtenerNombreUsuarioPorId(requestData["usuario_id"])
        # solicitante = self.userRepository.obtenerNombreUsuarioPorId(requestData.get("solicitante_id")) if requestData.get("solicitante_id") else None
        # tarea = None
        # if actividad and formaPago and responsable and coordinador and usuario:
        #     solicitudData = {
        #         **requestData,
        #         "actividad_id": actividad,
        #         "formaPago_id": formaPago,
        #         "responsable_id": responsable,
        #         "coordinador_id": coordinador,
        #         "usuario_id": usuario,
        #         "tarea_id": tarea,
        #         "solicitante_id": solicitante
        #     }
        return self.solicitudViajeRepository.crearSolicitudViaje(requestData)
        # else:
        #     return None