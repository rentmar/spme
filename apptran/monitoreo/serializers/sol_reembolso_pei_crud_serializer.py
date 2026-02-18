import re
from rest_framework import serializers
from spme_monitoreo.models import SolicitudReembolsoActPei
#from spme_monitoreo.models import SolicitudFondosActPei


class DetalleDestinoFondosItemSerializer(serializers.Serializer):
    """
    Serializer para validar cada item individual de detalleDestinoFondos
    """
    fecha = serializers.CharField(required=True, max_length=10)
    partida = serializers.CharField(required=True, max_length=100)
    factura_recibo = serializers.CharField(required=True, max_length=100)
    concepto = serializers.CharField(required=True, max_length=500)
    monto = serializers.FloatField(required=True, min_value=0)
    
    def validate_fecha(self, value):
        """
        Valida que la fecha tenga formato ISO 8601 (YYYY-MM-DD)
        """
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', value):
            raise serializers.ValidationError(
                "La fecha debe tener formato ISO 8601: YYYY-MM-DD (ej: 2026-01-02)"
            )
        return value


class DetalleDestinoFondosSerializer(serializers.Serializer):
    """
    Serializer para validar la estructura completa de detalleDestinoFondos
    """
    items = DetalleDestinoFondosItemSerializer(many=True, required=True)
    
    def validate_items(self, value):
        if not value or len(value) == 0:
            raise serializers.ValidationError(
                "Debe incluir al menos un item en detalleDestinoFondos"
            )
        return value


class SolicitudReembolsoActPeiSerializer(serializers.ModelSerializer):
    detalleDestinoFondos = DetalleDestinoFondosSerializer(required=False, allow_null=True)
    
    class Meta:
        model = SolicitudReembolsoActPei
        fields = '__all__'


class SolicitudReembolsoActPeiObtenerPorIdSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class SolicitudReembolsoActPeiFiltrarSerializer(serializers.Serializer):
    actividad_id = serializers.IntegerField(required=False)
    usuario_id = serializers.IntegerField(required=False)
    tarea_id = serializers.IntegerField(required=False, allow_null=True)


class SolicitudReembolsoActPeiActualizarEstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudReembolsoActPei
        fields = ['validacionResponsable', 'validacionCoordinador']
