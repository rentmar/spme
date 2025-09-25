# D:\proyecto_smpe\spme\spme_monitoreo\domain\models\response\solicitudViajeCompletaResponse.py
from rest_framework import serializers

class CreateSolicitudViajeCompletaResponse(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    mensaje = serializers.CharField(required=True)
    numeroFormulario = serializers.CharField(required=False)