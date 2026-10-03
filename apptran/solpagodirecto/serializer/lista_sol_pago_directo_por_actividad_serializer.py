# serializers.py 
from rest_framework import serializers
from spme_monitoreo.models import SolicitudPagoDirecto, FormaPago
from spme_autenticacion.models import Usuario
from ..services.estado_solicitud_service import EstadoSolicitudService

#Servicio de consolidacion
from spme_validaciones.services.consolidacion.service import ConsolidacionValidacionService
from spme_validaciones.services.consolidacion.modelos import MetodoResolucion


class SolicitudPagoDirectoSimpleSerializer(serializers.ModelSerializer):
    """Serializador simplificado para listar solicitudes de pago directo"""
    
    # Información del usuario que creó la solicitud
    solicitante = serializers.SerializerMethodField()
    # Información de validaciones
    estado_validacion = serializers.SerializerMethodField()
    # Nombre de la forma de pago
    forma_pago_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = SolicitudPagoDirecto
        fields = [
            'id',
            'numeroFormulario',
            'detalleDestinoFondos',
            'formaPago',
            'forma_pago_nombre',
            'lugarSolicitud',
            'fechaSolicitud',
            'montoSolicitado',
            'fechaRealizacionActividad',
            'descripcion_actividad',
            'objetivo_actividad',
            'datos_forma_pago',
            'bloquearIconosSolFondos',
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
        Calcula el estado consolidado en memoria
        """
        # estado = EstadoSolicitudService.get_estado_actual(obj)
        # return EstadoSolicitudService.get_estado_display(estado)
        #Recuperamos las validaciones pre cargadas
        validaciones_memoria = list(obj.validaciones.all())
        #Iniciar el servicio
        service = ConsolidacionValidacionService()
        #Evaluacion en memoria
        estado_consolidado = service.consolidar_desde_validaciones(
            tipo_solicitud="SOLICITUD_PAGO_DIRECTO",
            validaciones=validaciones_memoria,
            metodo_resolucion=MetodoResolucion.DECISORIO,
        )
        return estado_consolidado
        
    def get_forma_pago_nombre(self, obj):
        return obj.formaPago.formaPago if obj.formaPago else 'No especificada'