from rest_framework import serializers

class CreateSolicitudViajeResponse(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    mensaje = serializers.CharField(required=False, allow_blank=True, max_length=150)
    numero_formulario = serializers.CharField(required=False, allow_blank=True, max_length=150)

class ObtenerSolicitudesViajeResponse(serializers.Serializer):
    """
    Response para obtener solicitudes de viaje
    """
    estado = serializers.CharField(required=False, max_length=50)
    solicitudes = serializers.ListField(required=False, allow_null=True)
    mensaje = serializers.CharField(required=False, allow_blank=True, max_length=150)