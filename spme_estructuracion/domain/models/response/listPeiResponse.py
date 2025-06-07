from rest_framework import serializers
    
class PeiResponse(serializers.Serializer):
    id = serializers.IntegerField(max_value=999999)
    titulo = serializers.CharField(max_length=255)
    descripcion = serializers.CharField(max_length=1000, allow_blank=True)
    fecha_creacion = serializers.DateField()
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField()
    esta_vigente = serializers.BooleanField(default=True)
    creado_el = serializers.DateTimeField()
    modificado_el = serializers.DateTimeField()

class ListaPeiResponse(serializers.Serializer):
    lista_pei = serializers.ListField(child=PeiResponse())