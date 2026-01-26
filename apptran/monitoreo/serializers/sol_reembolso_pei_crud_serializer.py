from rest_framework import serializers
from spme_monitoreo.models import SolicitudReembolsoActPei
#from spme_monitoreo.models import SolicitudFondosActPei

class SolicitudReembolsoActPeiSerializer(serializers.ModelSerializer):
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
