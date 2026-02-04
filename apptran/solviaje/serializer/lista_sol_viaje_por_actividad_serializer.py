# serializers.py (en la misma carpeta)
from rest_framework import serializers
from spme_monitoreo.models import SolicitudViaje, FormaPago
from spme_autenticacion.models import Usuario
 
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
        if obj.validacionResponsable and obj.validacionCoordinador:
            return 'validada_completamente'
        elif obj.validacionResponsable:
            return 'validada_parcialmente'
        elif obj.validacionCoordinador:
            return 'rechazada'
        else:
            return 'pendiente'
    
    def get_forma_pago_nombre(self, obj):
        return obj.formaPago.formaPago if obj.formaPago else 'No especificada'