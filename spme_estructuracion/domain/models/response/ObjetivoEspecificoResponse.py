from rest_framework import serializers

class ObjetivoEspecificoResponse(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    codigo = serializers.CharField(required=False, allow_blank=True, max_length=50)
    descripcion = serializers.CharField(required=False, allow_blank=True, max_length=250)
    supuestos = serializers.CharField(required=False, allow_blank=True, max_length=250)
    riesgos = serializers.CharField(required=False, allow_blank=True, max_length=250)
    proyecto_id = serializers.IntegerField(required=False, allow_null=True)

class ObjetivoEspecificoResponseList(serializers.Serializer):
     objetivo_especifico_lista = serializers.ListField(child=ObjetivoEspecificoResponse())