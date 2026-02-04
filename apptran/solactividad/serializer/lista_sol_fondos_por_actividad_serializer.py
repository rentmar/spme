# serializers.py
from rest_framework import serializers
from spme_monitoreo.models import SolicitudFondos, FormaPago
from spme_autenticacion.models import Usuario
# serializers.py
from rest_framework import serializers

class SolicitudFondosSimpleSerializer(serializers.ModelSerializer):
    """Serializador simplificado para listar solicitudes"""
    
    # Información del usuario que creó la solicitud
    solicitante = serializers.SerializerMethodField()
    # Información de validaciones
    estado_validacion = serializers.SerializerMethodField()
    # Nombre de la forma de pago
    forma_pago_nombre = serializers.SerializerMethodField()
    
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
            'tarea'  # Incluimos para verificar que sea null
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
            return 'completamente_validada'
        elif obj.validacionResponsable and not obj.validacionCoordinador:
            return 'parcialmente_validada'
        elif not obj.validacionResponsable and obj.validacionCoordinador:
            return 'validacion_inversa'  # Caso poco común
        else:
            return 'pendiente'
    
    def get_forma_pago_nombre(self, obj):
        return obj.formaPago.formaPago if obj.formaPago else 'No especificada'