 # serializers.py
from rest_framework import serializers
from spme_monitoreo.models import SolicitudPagoDirecto, FormaPago
from spme_autenticacion.models import Usuario

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