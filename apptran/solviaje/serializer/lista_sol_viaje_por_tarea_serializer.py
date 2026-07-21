from rest_framework import serializers
from spme_autenticacion.models import Usuario
from spme_monitoreo.models import SolicitudViaje, FormaPago
from ..services.estado_solicitud_service import EstadoSolicitudService
 
class SolicitudViajeSerializer(serializers.ModelSerializer):
    solicitante = serializers.SerializerMethodField()
    forma_pago_nombre = serializers.SerializerMethodField()
    estado_validacion = serializers.SerializerMethodField()
    
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
            'solicitante',
            'validacionResponsable',
            'validacionCoordinador',
            'estado_validacion',
            'actividad',
            'tarea',
            'datos_forma_pago'
        ]
    
    def get_solicitante(self, obj):
        if obj.usuario:
            return {
                'id': obj.usuario.id,
                'nombre_completo': obj.usuario.get_full_name(),
                'cargo': obj.usuario.cargo
            }
        return None
    
    def get_forma_pago_nombre(self, obj):
        return obj.formaPago.formaPago if obj.formaPago else None
    
    def get_estado_validacion(self, obj):
        estado = EstadoSolicitudService.get_estado_actual(obj)
        return EstadoSolicitudService.get_estado_display(estado)