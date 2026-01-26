from rest_framework import serializers
from ..models import (
    ProyectoFonFosc, Institucion, ObjetivoFonfosc, 
    ResultadoFonfosc, IndicadorFonFosc, IndicadorObjetivoFonFosc
)


class InstitucionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institucion
        fields = [
            'id', 'sigla', 'nombre', 'emailInstitucion', 
            'telefono', 'direccion', 'casillaPostal', 'webSite'
        ]


class IndicadorFonFoscSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorFonFosc
        fields = '__all__'


class IndicadorObjetivoFonFoscSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorObjetivoFonFosc
        fields = '__all__'


class ResultadoFonfoscSerializer(serializers.ModelSerializer):
    # Indicadores del resultado
    indicadores_resultado = IndicadorFonFoscSerializer(
        source='indicador_resultado_fonfosc', 
        many=True, 
        read_only=True
    )
    
    class Meta:
        model = ResultadoFonfosc
        fields = [
            'id', 'codigo', 'descripcion', 'supuestosRiesgos', 
            'objetivo', 'indicadores_resultado'
        ]


class ObjetivoFonfoscSerializer(serializers.ModelSerializer):
    # Resultados del objetivo
    resultados = ResultadoFonfoscSerializer(
        source='resultados_fonfosc', 
        many=True, 
        read_only=True
    )
    
    # Indicadores del objetivo
    indicadores_objetivo = IndicadorObjetivoFonFoscSerializer(
        source='indicador_objetivo_fonfosc', 
        many=True, 
        read_only=True
    )
    
    class Meta:
        model = ObjetivoFonfosc
        fields = [
            'id', 'codigo', 'redaccion', 'supuestosRiesgos', 
            'proyecto', 'resultados', 'indicadores_objetivo'
        ]


class ProyectoFonFoscSerializer(serializers.ModelSerializer):
    # Institución
    institucion_detalle = InstitucionSerializer(
        source='institucion', 
        read_only=True
    )
    
    # Objetivo del proyecto (OneToOne)
    objetivo = ObjetivoFonfoscSerializer(
        source='objetivo_general_fonfosc', 
        read_only=True
    )
    
    # Procedencia de fondos
    procedencia_fondos_list = serializers.SerializerMethodField()
    
    class Meta:
        model = ProyectoFonFosc
        fields = [
            'id', 'codigo', 'titulo', 'descripcion',
            'fecha_creacion', 'fecha_inicio', 'fecha_finalizacion',
            'categoria', 'cobertura_geografica', 'presupuesto', 'estado',
            'institucion', 'institucion_detalle', 'responsable', 'pei',
            'procedencia_fondos', 'procedencia_fondos_list', 'objetivo'
        ]
        depth = 1
    
    def get_procedencia_fondos_list(self, obj):
        return [{
            'id': pf.id,
            'nombre': pf.nombre if hasattr(pf, 'nombre') else str(pf)
        } for pf in obj.procedencia_fondos.all()]