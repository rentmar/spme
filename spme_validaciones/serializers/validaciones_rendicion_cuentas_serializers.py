from rest_framework import serializers
from ..models import ValidacionRendicionCuentas
from .validaciones_informes_actividad_subac_serializers import ValidacionBaseSerializer


class ValidacionRendicionCuentasSerializer(ValidacionBaseSerializer):
    """Serializer para validaciones de rendición de cuentas."""
    
    rendicion_codigo = serializers.CharField(
        source='rendicion.numeroFormulario', read_only=True
    )
    rendicion_monto_asignado = serializers.DecimalField(
        source='rendicion.montoAsignado', read_only=True, max_digits=12, decimal_places=2
    )
    rendicion_monto_descargado = serializers.DecimalField(
        source='rendicion.montoDescargado', read_only=True, max_digits=12, decimal_places=2
    )
    rendicion_saldo = serializers.DecimalField(
        source='rendicion.saldo', read_only=True, max_digits=12, decimal_places=2
    )
    rendicion_tipo = serializers.SerializerMethodField()
    
    class Meta(ValidacionBaseSerializer.Meta):
        model = ValidacionRendicionCuentas
        fields = ValidacionBaseSerializer.Meta.fields + [
            'rendicion', 'rendicion_codigo', 'rendicion_monto_asignado',
            'rendicion_monto_descargado', 'rendicion_saldo', 'rendicion_tipo'
        ]
    
    def get_rendicion_tipo(self, obj):
        return obj.tipo_rendicion
    
    def get_tipo_documento(self, obj):
        return 'RENDICION_CUENTAS'


class AsignarValidadoresRendicionCuentasSerializer(serializers.Serializer):
    """Serializer para asignar validadores a una rendición de cuentas."""
    
    validador_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    
    def validate_validador_ids(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError("No se permiten validador_ids duplicados")
        return value


class ResetearValidacionesRendicionCuentasSerializer(serializers.Serializer):
    """Serializer para resetear validaciones de rendición de cuentas."""
    
    nueva_version = serializers.CharField(default='2')