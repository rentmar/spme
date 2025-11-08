from rest_framework import serializers

class CreateSolicitudPagoDirectoResponse(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    mensaje = serializers.CharField(required=False, allow_blank=True, max_length=150)

class ObtenerSolicitudesPagoDirectoResponse(serializers.Serializer):
    """
    Response para obtener solicitudes de pago directo
    """
    estado = serializers.CharField(required=False, max_length=50)
    solicitudes = serializers.ListField(required=False, allow_null=True)
    mensaje = serializers.CharField(required=False, allow_blank=True, max_length=150)