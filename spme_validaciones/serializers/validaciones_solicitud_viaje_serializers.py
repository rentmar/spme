#spme/spme_validaciones/serializers/validaciones_solicitud_viaje_serializers.py
from rest_framework import serializers
from ..models import ValidacionSolicitudViaje
from .validaciones_informes_actividad_subac_serializers import ValidacionBaseSerializer


class ValidacionSolicitudViajeSerializer(ValidacionBaseSerializer):
    """Serializer para validaciones de solicitud de viaje."""
    
    solicitud_codigo = serializers.CharField(
        source='solicitud.numeroFormulario', read_only=True
    )
    solicitud_monto = serializers.DecimalField(
        source='solicitud.montoSolicitado', read_only=True, max_digits=12, decimal_places=2
    )
    solicitud_tipo = serializers.SerializerMethodField()
    solicitud_evento = serializers.CharField(
        source='solicitud.evento', read_only=True
    )
    solicitud_lugar = serializers.CharField(
        source='solicitud.lugarEvento', read_only=True
    )
    
    class Meta(ValidacionBaseSerializer.Meta):
        model = ValidacionSolicitudViaje
        fields = ValidacionBaseSerializer.Meta.fields + [
            'solicitud', 'solicitud_codigo', 'solicitud_monto', 'solicitud_tipo',
            'solicitud_evento', 'solicitud_lugar'
        ]
    
    def get_solicitud_tipo(self, obj):
        return obj.tipo_solicitud
    
    def get_tipo_documento(self, obj):
        return 'SOLICITUD_VIAJE'


class AsignarValidadoresSolicitudViajeSerializer(serializers.Serializer):
    """Serializer para asignar validadores a una solicitud de viaje."""
    
    validador_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    
    def validate_validador_ids(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError("No se permiten validador_ids duplicados")
        return value


class ResetearValidacionesSolicitudViajeSerializer(serializers.Serializer):
    """Serializer para resetear validaciones de solicitud de viaje."""
    
    nueva_version = serializers.CharField(default='2')