from spme_monitoreo.container.repositoryContainer import SolicitudReembolsoRepositoryContainer, FormaPagoRepositoryContainer
from spme_autenticacion.container.repositoryContainer import UserRepositoryContainer
from spme_actividades.container.repositoryContainer import ActividadesRepositoryContainer

class CrearSolicitudReembolsoUseCase:
    def __init__(self):
        self.contenedor = SolicitudReembolsoRepositoryContainer()
        self.solicitudReembolsoRepository = self.contenedor.solicitudReembolsoRepository()
        self.contenedorFormaPago = FormaPagoRepositoryContainer()
        self.formaPagoRepository = self.contenedorFormaPago.formaPagoRepository()
        self.contenedorUser = UserRepositoryContainer()
        self.userRepository = self.contenedorUser.userRepository()
        self.contenedorActividad = ActividadesRepositoryContainer()
        self.actividadesRepository = self.contenedorActividad.actividadesRepository()

    def execute(self, requestData):
        """
        Crea una nueva solicitud de reembolso.

        :param requestData: Datos de la solicitud de reembolso.
        :return: Resultado de la creación de la solicitud.
        """
        # Obtener las relaciones si se proporcionan los IDs
        forma_pago = None
        if requestData.get("formaPago_id"):
            forma_pago = self.formaPagoRepository.obtenerFormaPagoPorId(requestData["formaPago_id"])
        
        contador = None
        if requestData.get("contador_id"):
            contador = self.userRepository.obtenerUsuarioPorId(requestData["contador_id"])
        
        coordinador = None
        if requestData.get("coordinador_id"):
            coordinador = self.userRepository.obtenerUsuarioPorId(requestData["coordinador_id"])
        
        usuario = None
        if requestData.get("usuario_id"):
            usuario = self.userRepository.obtenerUsuarioPorId(requestData["usuario_id"])
        
        actividad = None
        if requestData.get("actividad_id"):
            # Obtener la actividad y asegurarse de que sea una instancia individual
            actividad_result = self.actividadesRepository.obtenerActividadPorId(requestData["actividad_id"])
            # Si devuelve un QuerySet, tomar el primer elemento
            if hasattr(actividad_result, '__iter__') and not isinstance(actividad_result, str):
                actividad = actividad_result.first() if actividad_result else None
            else:
                actividad = actividad_result
        
        # Preparar los datos para crear la solicitud
        solicitudData = {
            "detalleDestinoFondos": requestData.get("detalleDestinoFondos"),
            "formaPago": forma_pago,
            "lugarSolicitud": requestData.get("lugarSolicitud"),
            "fechaSolicitud": requestData.get("fechaSolicitud"),
            "fechaRealizacionActividad": requestData.get("fechaRealizacionActividad"),
            "montoSolicitado": requestData.get("montoSolicitado"),
            "validacionContador": requestData.get("validacionResponsable", False),
            "contador": contador,
            "validacionCoordinador": requestData.get("validacionCoordinador", False),
            "coordinador": coordinador,
            "usuario": usuario,
            "actividad": actividad,
            "descripcion_actividad": requestData.get("descripcion_actividad"),
            "objetivo_actividad": requestData.get("objetivo_actividad"),
            "datos_forma_pago": requestData.get("datos_forma_pago"),
            "bloquearIconos": requestData.get("bloquearIconos", True)
        }
        
        return self.solicitudReembolsoRepository.crearSolicitudReembolso(solicitudData)
    
    def obtenerSolicitudReembolso(self, filtros):
        """
        Obtiene solicitudes de reembolso con filtros
        :param filtros: Diccionario con filtros (id_solicitudReembolso, id_actividad, id_tarea, usuario)
        :return: Lista de solicitudes de reembolso
        """
        return self.solicitudReembolsoRepository.obtenerSolicitudReembolso(filtros)