# serializers.py
from rest_framework import serializers
from spme_estructuracion_proyecto.models import ( 
    Proyecto, ObjetivoGeneralProyecto, ObjetivoEspecificoProyecto,
    ResultadoOG, ResultadoOE, ProductoResultadoOE, 
    IndicadorObjetivoGeneral, IndicadorResultadoObjGral,
    IndicadorObjetivoEspecifico, IndicadorResultadoObjEspecifico
    )

class IndicadorOGSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorObjetivoGeneral
        fields = ['id', 'codigo', 'descripcion', 'tipo', 'frecuencia', 'baseline']

class IndicadorResultadoOGSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorResultadoObjGral
        fields = ['id', 'codigo', 'descripcion', 'tipo', 'frecuencia', 'baseline']

class ResultadoOGSerializer(serializers.ModelSerializer):
    indicadores = IndicadorResultadoOGSerializer(many=True, read_only=True, source='indicador_res_og')
    
    class Meta:
        model = ResultadoOG
        fields = ['id', 'codigo', 'descripcion', 'indicadores']

class ObjetivoGeneralSerializer(serializers.ModelSerializer):
    indicadores = IndicadorOGSerializer(many=True, read_only=True, source='indicador_og')
    resultados = ResultadoOGSerializer(many=True, read_only=True, source='resultados_og')
    
    class Meta:
        model = ObjetivoGeneralProyecto
        fields = ['id', 'codigo', 'descripcion', 'indicadores', 'resultados']

class ProductoResultadoOESerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoResultadoOE
        fields = ['id', 'codigo', 'descripcion', 'entregado']

class IndicadorOESerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorObjetivoEspecifico
        fields = ['id', 'codigo', 'descripcion', 'tipo', 'frecuencia', 'baseline']

class IndicadorResultadoOESerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorResultadoObjEspecifico
        fields = ['id', 'codigo', 'descripcion', 'tipo', 'frecuencia', 'baseline']

class ResultadoOESerializer(serializers.ModelSerializer):
    indicadores = IndicadorResultadoOESerializer(many=True, read_only=True, source='indicador_res_oe')
    productos = ProductoResultadoOESerializer(many=True, read_only=True, source='productos_res_oe')
    
    class Meta:
        model = ResultadoOE
        fields = ['id', 'codigo', 'descripcion', 'indicadores', 'productos']

class ObjetivoEspecificoSerializer(serializers.ModelSerializer):
    indicadores = IndicadorOESerializer(many=True, read_only=True, source='indicador_oe')
    resultados = ResultadoOESerializer(many=True, read_only=True, source='resultados_oe')
    
    class Meta:
        model = ObjetivoEspecificoProyecto
        fields = ['id', 'codigo', 'descripcion', 'indicadores', 'resultados']

class EstructuraJerarquicaSerializer(serializers.ModelSerializer):
    objetivo_general = ObjetivoGeneralSerializer(read_only=True)
    objetivos_especificos = ObjetivoEspecificoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Proyecto
        fields = [
            'id', 'codigo', 'titulo', 'descripcion', 'estado',
            'objetivo_general', 'objetivos_especificos'
        ]