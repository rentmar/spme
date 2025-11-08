from rest_framework import serializers

class ActualizarValidacionSolicitudPagoDirectoResponse(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    mensaje = serializers.CharField(required=False, allow_blank=True, max_length=150)
    validacion_responsable = serializers.BooleanField(required=False)
    validacion_coordinador = serializers.BooleanField(required=False)