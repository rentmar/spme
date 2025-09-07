from rest_framework import serializers
from spme_estructuracion_proyecto.models import (
    DiagramaEstructura, Proyecto, ObjetivoGeneralProyecto, ObjetivoEspecificoProyecto,
    ResultadoOG, ResultadoOE, Proceso, ProductoOE, ProductoResultadoOE
)

class DiagramaEstructuraSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagramaEstructura
        fields = '__all__'

class ProyectoSerializer(serializers.ModelSerializer):
    fecha_inicio = serializers.DateField(
        input_formats=['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', 'iso-8601'],
        required=False,
        allow_null=True
    )
    fecha_finalizacion = serializers.DateField(
        input_formats=['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', 'iso-8601'],
        required=False,
        allow_null=True
    )
    fecha_creacion = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Proyecto
        fields = '__all__'

class ObjetivoGeneralSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjetivoGeneralProyecto
        fields = '__all__'

class ObjetivoEspecificoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjetivoEspecificoProyecto
        fields = '__all__'

class ResultadoOGSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultadoOG
        fields = '__all__'

class ResultadoOESerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultadoOE
        fields = '__all__'

class ProcesoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proceso
        fields = '__all__'

class ProductoOESerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoOE
        fields = '__all__'

class ProductoResultadoOESerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoResultadoOE
        fields = '__all__'
