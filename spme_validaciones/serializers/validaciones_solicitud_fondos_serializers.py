#spme/spme_validaciones/serializers/validaciones_solicitud_fondos_serializers.py
from rest_framework import serializers
from ..models import ValidacionSolicitudFondos
from .validaciones_informes_actividad_subac_serializers import ValidacionBaseSerializer


class ValidacionSolicitudFondosSerializer(ValidacionBaseSerializer):
    """Serializer para validaciones de solicitud de fondos."""
    
    solicitud_codigo = serializers.CharField(
        source='solicitud.numeroFormulario', read_only=True
    )
    solicitud_monto = serializers.DecimalField(
        source='solicitud.montoSolicitado', read_only=True, max_digits=12, decimal_places=2
    )
    solicitud_tipo = serializers.SerializerMethodField()
    
    class Meta(ValidacionBaseSerializer.Meta):
        model = ValidacionSolicitudFondos
        fields = ValidacionBaseSerializer.Meta.fields + [
            'solicitud', 'solicitud_codigo', 'solicitud_monto', 'solicitud_tipo'
        ]
    
    def get_solicitud_tipo(self, obj):
        return obj.tipo_solicitud
    
    def get_tipo_documento(self, obj):
        return 'SOLICITUD_FONDOS'


class AsignarValidadoresSolicitudFondosSerializer(serializers.Serializer):
    """Serializer para asignar validadores a una solicitud de fondos."""
    
    validador_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    
    def validate_validador_ids(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError("No se permiten validador_ids duplicados")
        return value


class ResetearValidacionesSolicitudFondosSerializer(serializers.Serializer):
    """Serializer para resetear validaciones de solicitud de fondos."""
    
    nueva_version = serializers.CharField(default='2')