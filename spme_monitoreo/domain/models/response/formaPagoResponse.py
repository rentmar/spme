from rest_framework import serializers

class ObtenerFormaPagoResponse(serializers.Serializer):
    """
    Response para obtener formas de pago
    """
    estado = serializers.CharField(required=False, max_length=50)
    formasPago = serializers.ListField(required=False, allow_null=True)
    mensaje = serializers.CharField(required=False, allow_blank=True, max_length=150)