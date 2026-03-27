# serializers.py
from rest_framework import serializers
from spme_monitoreo.models import  FormaPago, SolicitudFondos
from spme_actividades.models import Actividad, TareaActividad
from spme_autenticacion.models import Usuario


class SolicitudFondosSerializer(serializers.ModelSerializer):
    solicitante = serializers.SerializerMethodField()
    forma_pago_nombre = serializers.SerializerMethodField()
    estado_validacion = serializers.SerializerMethodField()
    
    class Meta:
        model = SolicitudFondos
        fields = [
            'id',
            'numeroFormulario',
            'fechaSolicitud',
            'montoSolicitado',
            'descripcion_actividad',
            'lugarSolicitud',
            'solicitante',
            'validacionResponsable',
            'validacionCoordinador',
            'estado_validacion',
            'formaPago',
            'forma_pago_nombre',
            'fechaRealizacionActividad',
            'bloquearIconosSolFondos',
            'actividad',
            'tarea',
            'detalleDestinoFondos',
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