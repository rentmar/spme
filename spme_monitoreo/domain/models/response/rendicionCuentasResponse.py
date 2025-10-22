from rest_framework import serializers

class CreateRendicionFondosResponse(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    mensaje = serializers.CharField(required=False, allow_blank=True, max_length=150)

class ObtenerRendicionDeCuentasResponse(serializers.Serializer):
    """
    Response para obtener rendiciones de cuentas
    """
    estado = serializers.CharField(required=False, max_length=50)
    rendiciones = serializers.ListField(required=False, allow_null=True)
    mensaje = serializers.CharField(required=False, allow_blank=True, max_length=150)
