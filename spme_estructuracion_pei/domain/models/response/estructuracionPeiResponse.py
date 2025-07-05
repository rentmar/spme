from rest_framework import serializers

class CreateEstructuraPeiResponse(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    mensaje = serializers.CharField(required=False, allow_blank=True, max_length=150)

class ObtenerEstructuraPeiResponse(serializers.Serializer):
    id = serializers.IntegerField()
    titulo = serializers.CharField(max_length = 150)
    descripcion  = serializers.CharField(max_length = 500)
    fecha_creacion = serializers.DateTimeField()
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField()
    esta_vigente = serializers.BooleanField()
    creado_el = serializers.DateTimeField()
    modificado_el = serializers.DateTimeField()