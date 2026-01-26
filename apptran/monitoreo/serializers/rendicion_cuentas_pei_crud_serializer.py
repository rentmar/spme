from rest_framework import serializers
from spme_monitoreo.models import RendicionCuentasActPei


class RendicionCuentasActPeiSerializer(serializers.ModelSerializer):
    class Meta:
        model = RendicionCuentasActPei
        fields = '__all__'


# Serializer para filtrar por ID
class RendicionCuentasActPeiObtenerPorIdSerializer(serializers.Serializer):
    id = serializers.IntegerField()


# Serializer para filtrar por actividad_id, usuario_id, tarea_id
class RendicionCuentasActPeiFiltrarSerializer(serializers.Serializer):
    actividad_id = serializers.IntegerField(required=False)
    usuario_id = serializers.IntegerField(required=False)
    tarea_id = serializers.IntegerField(required=False, allow_null=True)


# Serializer para actualizar estado de validación
class RendicionCuentasActPeiActualizarEstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RendicionCuentasActPei
        fields = ['validacionResponsable', 'validacionCoordinador']