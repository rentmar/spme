from rest_framework import serializers
from spme_estructuracion_proyecto.models import (
    IndicadorObjetivoGeneral,
    IndicadorResultadoObjGral,
    IndicadorObjetivoEspecifico,
    IndicadorResultadoObjEspecifico,
)

class IndicadorBaseSerializer(serializers.ModelSerializer):
    tipo_indicador = serializers.SerializerMethodField()
    
    class Meta:
        model = None
        fields = ['id', 'codigo', 'descripcion', 'redaccion', 'fuente_verificacion', 
                 'tipo', 'frecuencia', 'responsable', 'baseline', 'fechaLineaBase',
                 'target_q1', 'fechaTargetQ1', 'target_q2', 'fechaTargetQ2',
                 'target_q3', 'fechaTargetQ3', 'target_q4', 'fechaTargetQ4',
                 'target_poblacion', 'fechaTargetPoblacion', 'tipo_indicador']
    
    def get_tipo_indicador(self, obj):
        if hasattr(obj, 'objetivo_general'): return 'OG'
        if hasattr(obj, 'resultado_og'): return 'ROG'
        if hasattr(obj, 'objetivo_especifico'): return 'OE'
        if hasattr(obj, 'resultado_obj_especifico'): return 'ROE'
        return 'IND'

class IndicadorObjetivoGeneralSerializer(IndicadorBaseSerializer):
    class Meta(IndicadorBaseSerializer.Meta):
        model = IndicadorObjetivoGeneral
        fields = IndicadorBaseSerializer.Meta.fields + ['objetivo_general_id']

class IndicadorResultadoObjGralSerializer(IndicadorBaseSerializer):
    class Meta(IndicadorBaseSerializer.Meta):
        model = IndicadorResultadoObjGral
        fields = IndicadorBaseSerializer.Meta.fields + ['resultado_og_id']

class IndicadorObjetivoEspecificoSerializer(IndicadorBaseSerializer):
    class Meta(IndicadorBaseSerializer.Meta):
        model = IndicadorObjetivoEspecifico
        fields = IndicadorBaseSerializer.Meta.fields + ['objetivo_especifico_id']

class IndicadorResultadoObjEspecificoSerializer(IndicadorBaseSerializer):
    class Meta(IndicadorBaseSerializer.Meta):
        model = IndicadorResultadoObjEspecifico
        fields = IndicadorBaseSerializer.Meta.fields + ['resultado_obj_especifico_id']