from rest_framework import serializers

class CreateSolicitudPagoDirectoResponse(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    mensaje = serializers.CharField(required=False, allow_blank=True, max_length=150)