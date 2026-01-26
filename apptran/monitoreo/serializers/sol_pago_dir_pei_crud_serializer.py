from rest_framework import serializers
from spme_monitoreo.models import SolicitudPagoDirectoActPei


class SolicitudPagoDirectoActPeiSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudPagoDirectoActPei
        fields = '__all__'


# Serializer para endpoint #3: Obtener por ID
class SolicitudPagoDirectoActPeiObtenerPorIdSerializer(serializers.Serializer):
    id = serializers.IntegerField()


# Serializer para endpoint #4: Filtrar
class SolicitudPagoDirectoActPeiFiltrarSerializer(serializers.Serializer):
    actividad_id = serializers.IntegerField(required=False)
    usuario_id = serializers.IntegerField(required=False)
    tarea_id = serializers.IntegerField(required=False, allow_null=True)


# Serializer para endpoint #5: Actualizar estado
class SolicitudPagoDirectoActPeiActualizarEstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudPagoDirectoActPei
        fields = ['validacionResponsable', 'validacionCoordinador']