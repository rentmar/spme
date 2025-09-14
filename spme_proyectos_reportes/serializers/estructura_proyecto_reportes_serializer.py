from rest_framework import serializers
from spme_actividades.models import *
from spme_estructuracion_proyecto.models import *


class ProductoROESerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoResultadoOE
        fields = ['id', 'codigo', 'descripcion']

class ResultadoOESerializer(serializers.ModelSerializer):
    productos_res_oe = ProductoROESerializer(many=True, read_only=True)
    
    class Meta:
        model = ResultadoOE
        fields = ['id', 'codigo', 'descripcion', 'productos_res_oe']

class ProductoOESerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoOE
        fields = ['id', 'codigo', 'descripcion']

class ObjetivoEspecificoSerializer(serializers.ModelSerializer):
    resultados_oe = ResultadoOESerializer(many=True, read_only=True)
    productos_oe = ProductoOESerializer(many=True, read_only=True)
    
    class Meta:
        model = ObjetivoEspecificoProyecto
        fields = ['id', 'codigo', 'descripcion', 'resultados_oe', 'productos_oe']

class ResultadoOGSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultadoOG
        fields = ['id', 'codigo', 'descripcion']

class ObjetivoGeneralSerializer(serializers.ModelSerializer):
    resultados_og = ResultadoOGSerializer(many=True, read_only=True)
    objetivos_especificos = serializers.SerializerMethodField()
    
    class Meta:
        model = ObjetivoGeneralProyecto
        fields = ['id', 'codigo', 'descripcion', 'resultados_og', 'objetivos_especificos']
    
    def get_objetivos_especificos(self, obj):
        # Solo objetivos específicos relacionados con este objetivo general
        objetivos_especificos = obj.objetivos_especificos_og.all()
        return ObjetivoEspecificoSerializer(objetivos_especificos, many=True).data

class ActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actividad
        fields = ['id', 'codigo', 'nombreCorto']

class ProyectoDetailSerializer(serializers.ModelSerializer):
    objetivo_general = ObjetivoGeneralSerializer(read_only=True)
    actividades = serializers.SerializerMethodField()
    
    class Meta:
        model = Proyecto
        fields = [
            'id', 'codigo', 'titulo', 'objetivo_general', 
            'actividades'
        ]
    
    def get_actividades(self, obj):
        actividades = obj.actividad_proyecto.all()
        return ActividadSerializer(actividades, many=True).data