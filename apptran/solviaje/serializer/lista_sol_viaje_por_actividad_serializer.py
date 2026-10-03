# serializers.py (en la misma carpeta)
from rest_framework import serializers
from spme_monitoreo.models import SolicitudViaje, FormaPago
from spme_autenticacion.models import Usuario
from ..services.estado_solicitud_service import EstadoSolicitudService

#Importar el nuevo servicio de consolidacion
from spme_validaciones.services.consolidacion.service import ConsolidacionValidacionService
from spme_validaciones.services.consolidacion.modelos import MetodoResolucion


class SolicitudViajeSimpleSerializer(serializers.ModelSerializer):
    """Serializador simplificado para listar solicitudes de viaje"""
    
    # Información del usuario que creó la solicitud
    solicitante = serializers.SerializerMethodField()
    # Información de validaciones
    estado_validacion = serializers.SerializerMethodField()
    # Nombre de la forma de pago
    forma_pago_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = SolicitudViaje
        fields = [
            'id',
            'numeroFormulario',
            'evento',
            'lugarEvento',
            'institucionesParticipantes',
            'organizador',
            'quienCubreGastos',
            'justificacionAsistencia',
            'fondosUnitas',
            'tareasPrevias',
            'bloquearIconos',
            'formaPago',
            'forma_pago_nombre',
            'montoSolicitado',
            'lugarSolicitud',
            'fechaSolicitud',
            'fechaEvento',
            'detalleGasto',
            'datos_forma_pago',
            'solicitante',
            'validacionResponsable',
            'validacionCoordinador',
            'estado_validacion',
            'actividad',
            'tarea'
        ]
    
    def get_solicitante(self, obj):
        if obj.usuario:
            return {
                'id': obj.usuario.id,
                'nombre_completo': obj.usuario.get_full_name(),
                'cargo': obj.usuario.cargo
            }
        return None
    
    def get_estado_validacion(self, obj):
        """
        Calcula el estado de consolidacion/validacion
        """
        # estado = EstadoSolicitudService.get_estado_actual(obj)
        # return EstadoSolicitudService.get_estado_display(estado)
        # Recuperar las validaciones pre-cargadas
        validaciones_memoria = list(obj.validaciones.all())
        # Inicia el servicio
        service = ConsolidacionValidacionService()
        #Evaluar en memoria
        estado_consolidado = service.consolidar_desde_validaciones(
            tipo_solicitud="SOLICITUD_VIAJE",
            validaciones=validaciones_memoria,
            metodo_resolucion=MetodoResolucion.DECISORIO,
        ) 
        return estado_consolidado
    
    def get_forma_pago_nombre(self, obj):
        return obj.formaPago.formaPago if obj.formaPago else 'No especificada'