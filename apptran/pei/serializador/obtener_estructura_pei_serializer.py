# serializers.py
from rest_framework import serializers
from django.db.models import Q
from spme_estructuracion_pei.models import (
    Pei, ObjetivoPei, FactoresCriticos, 
    IndicadorPeiBase, IndicadorPeiCuantitativo, IndicadorPeiCualitativo
)

class FactoresCriticosSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactoresCriticos
        fields = ['id', 'factor_critico']

# Serializador común para campos base
class IndicadorBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorPeiBase
        fields = [
            'id', 'codigo', 'descripcion',
            'captura_informacion', 'responsabilidad',
            'frecuencia_recopilacion', 'uso_informacion'
        ]

# Extender el serializador base para cada tipo
class IndicadorCuantitativoDetailSerializer(IndicadorBaseSerializer):
    tipo = serializers.CharField(default='indicadorpeicuantitativo', read_only=True)
    numerador = serializers.CharField()
    denominador = serializers.CharField()
    umbral_des_numeral = serializers.IntegerField()
    
    class Meta(IndicadorBaseSerializer.Meta):
        model = IndicadorPeiCuantitativo
        fields = IndicadorBaseSerializer.Meta.fields + [
            'tipo', 'numerador', 'denominador', 'umbral_des_numeral',
            'umbral_des_literal_um1', 'umbral_des_literal_um2',
            'umbral_des_literal_um3'
        ]

class IndicadorCualitativoDetailSerializer(IndicadorBaseSerializer):
    tipo = serializers.CharField(default='indicadorpeicualitativo', read_only=True)
    
    class Meta(IndicadorBaseSerializer.Meta):
        model = IndicadorPeiCualitativo
        fields = IndicadorBaseSerializer.Meta.fields + [
            'tipo', 'umbral_des_literal_um1', 'umbral_des_literal_um2',
            'umbral_des_literal_um3'
        ]

class ObjetivoPeiSerializer(serializers.ModelSerializer):
    indicadores = serializers.SerializerMethodField()
    factores_criticos = FactoresCriticosSerializer(many=True, read_only=True)
    
    class Meta:
        model = ObjetivoPei
        fields = ['id', 'codigo', 'descripcion', 'indicadores', 'factores_criticos']
    
    def get_indicadores(self, obj):
        # Usar una sola consulta optimizada
        from django.db.models import Prefetch
        
        # Obtener todos los indicadores del objetivo con sus tipos específicos
        cuantitativos = obj.indicador_pei_objetivo.instance_of(IndicadorPeiCuantitativo)
        cualitativos = obj.indicador_pei_objetivo.instance_of(IndicadorPeiCualitativo)
        
        # Serializar cada tipo
        cuantitativos_data = IndicadorCuantitativoDetailSerializer(cuantitativos, many=True).data
        cualitativos_data = IndicadorCualitativoDetailSerializer(cualitativos, many=True).data
        
        # Combinar resultados
        combined = list(cuantitativos_data) + list(cualitativos_data)
        
        # Ordenar por código si existe, si no por ID
        combined.sort(key=lambda x: (x.get('codigo', ''), x.get('id', 0)))
        
        return combined

class PeiSerializer(serializers.ModelSerializer):
    objetivos = ObjetivoPeiSerializer(many=True, read_only=True, source='pei_obj_general')
    
    class Meta:
        model = Pei
        fields = [
            'id', 'titulo', 'descripcion', 'fecha_creacion',
            'fecha_inicio', 'fecha_fin', 'esta_vigente',
            'objetivos'
        ]