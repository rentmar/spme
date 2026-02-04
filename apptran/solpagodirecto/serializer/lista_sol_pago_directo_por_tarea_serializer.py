from rest_framework import serializers
from spme_monitoreo.models import SolicitudPagoDirecto, FormaPago
from spme_autenticacion.models import Usuario


class SolicitudPagoDirectoSerializer(serializers.ModelSerializer):
    solicitante = serializers.SerializerMethodField()
    forma_pago_nombre = serializers.SerializerMethodField()
    estado_validacion = serializers.SerializerMethodField()
    
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
    
    def get_forma_pago_nombre(self, obj):
        return obj.formaPago.formaPago if obj.formaPago else None
    
    def get_estado_validacion(self, obj):
        if obj.validacionResponsable and obj.validacionCoordinador:
            return 'validado_completamente'
        elif obj.validacionResponsable:
            return 'validado_parcialmente'
        elif obj.validacionCoordinador:
            return 'rechazado'
        else:
            return 'pendiente'