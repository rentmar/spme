# D:\proyecto_smpe\spme\spme_monitoreo\domain\usecases\solicitudViajeCompletaUseCase.py
from spme_monitoreo.container.repositoryContainer import SolicitudViajeRepositoryContainer
from spme_autenticacion.container.repositoryContainer import UserRepositoryContainer
from spme_actividades.container.repositoryContainer import ActividadesRepositoryContainer
import random
import string

class CrearSolicitudViajeCompletaUseCase:
    def __init__(self):
        self.solicitudViajeContainer = SolicitudViajeRepositoryContainer()
        self.userContainer = UserRepositoryContainer()
        self.actividadesContainer = ActividadesRepositoryContainer()
        
        self.solicitudViajeRepository = self.solicitudViajeContainer.solicitudViajeRepository()
        self.userRepository = self.userContainer.userRepository()
        self.actividadesRepository = self.actividadesContainer.actividadesRepository()

    def generate_form_number(self):
        """Genera un número de formulario único"""
        prefix = "SV-"
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return f"{prefix}{random_str}"

    def execute(self, requestData):
        try:
            # Obtener usuario solicitante
            usuario = self.userRepository.obtenerUsuarioPorId(requestData["idSolicitanteDeViaje"])
            if not usuario:
                return None

            # Obtener responsable y coordinador
            responsable = self.userRepository.obtenerUsuarioPorId(requestData["idresponsable"])
            coordinador = self.userRepository.obtenerUsuarioPorId(requestData["idcoordinador"])

            # Buscar forma de pago
            forma_pago_obj = None  # Aquí deberías implementar la lógica para buscar la forma de pago

            # Preparar datos para la solicitud de viaje
            solicitud_data = {
                "numeroFormulario": self.generate_form_number(),
                "evento": requestData["nombreEvento"],
                "fechaInicio": requestData["fechaEvento"],
                "fechaFin": requestData["fechaEvento"],  # Misma fecha si no se especifica fin
                "lugarEvento": requestData["lugarRealizacion"],
                "institucionesParticipantes": requestData["entidadesParticipantes"],
                "organizador": requestData["entidadOrganizadora"],
                "quienCubreGastos": requestData["entidadFinanciadora"],
                "justificacionAsistencia": requestData["justificacionAsistencia"],
                "fondosUnitas": requestData["fondoUnitas"],
                "tareasPrevias": requestData["tareasPrevias"],
                "montoSolicitado": requestData["montoTotal"],
                "formaPago": forma_pago_obj,
                "lugarSolicitud": requestData["lugarDeSolicitud"],
                "fechaSolicitud": requestData["fechaDeSolicitud"],
                "validacionResponsable": requestData["validacionResponsable"],
                "responsable": responsable,
                "validacionCoordinador": requestData["validacionCoordinador"],
                "coordinador": coordinador,
                "usuario": usuario,
                "detalleDestinoFondos": requestData["DetalleGasto"],
            }

            # Crear la solicitud de viaje
            solicitud_viaje = self.solicitudViajeRepository.crearSolicitudViaje(solicitud_data)
            
            return {
                "id": solicitud_viaje.id,
                "numeroFormulario": solicitud_viaje.numeroFormulario
            }

        except Exception as e:
            print(f"Error en CrearSolicitudViajeCompletaUseCase: {str(e)}")
            return None