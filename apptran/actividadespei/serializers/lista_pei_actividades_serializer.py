# serializers.py
from rest_framework import serializers
# from .models import ActividadPei, Pei, Usuario, ObjetivoPei, FactoresCriticos, IndicadorPeiCuantitativo, IndicadorPeiCualitativo

from spme_estructuracion_pei.models import (
    Pei,
    ActividadPei,
    ObjetivoPei,
    FactoresCriticos,
    IndicadorPeiCuantitativo,
    IndicadorPeiCualitativo,
)


class ObjetivoPeiSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjetivoPei
        fields = '__all__'

class FactorCriticoSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactoresCriticos
        fields = '__all__'

class IndicadorCuantitativoSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorPeiCuantitativo
        fields = '__all__'

class IndicadorCualitativoSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorPeiCualitativo
        fields = '__all__'

class ActividadPeiSerializer(serializers.ModelSerializer):
    responsable = serializers.CharField(source='responsable.username', read_only=True)
    tipo_valor = serializers.CharField(source='tipo.tipo_actividad', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    objetivos_pei = ObjetivoPeiSimpleSerializer(many=True, read_only=True)
    factores_criticos = FactorCriticoSimpleSerializer(many=True, read_only=True)
    indicadores_cuantitativos = IndicadorCuantitativoSimpleSerializer(many=True, read_only=True)
    indicadores_cualitativos = IndicadorCualitativoSimpleSerializer(many=True, read_only=True)
    
    class Meta:
        model = ActividadPei
        fields = [
            'id',
            'codigo',
            'nombreCorto',
            'descripcion',
            'supuestos',
            'riesgos',
            'objetivo_de_actividad',
            'descripcion_evaluacion',
            'descripcion_tipo_actividad',
            'fecha_programada',
            'fecha_inicio',
            'fecha_cierre',
            'presupuesto',
            'presupuestoGlobal',
            'totalReportado',
            'totalEjecutado',
            'saldo',
            'gradoEjecucion',
            'procedencia_fondos',
            'estado',
            'estado_display',
            'tipo',
            'tipo_valor',
            'pei',
            'responsable',  
            'estaInactiva',
            'objetivos_pei',
            'factores_criticos',
            'indicadores_cuantitativos',
            'indicadores_cualitativos',
        ]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Si tipo es null, usar NODEF como predeterminado
        if not instance.tipo and hasattr(instance, 'tipo'):
            data['tipo'] = getattr(instance, 'tipo', 'NODEF')
        
        # Si responsable es null, retornar string vacío
        if not instance.responsable:
            data['responsable'] = ''
        
        return data

class PeiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pei
        fields = ['id', 'titulo', 'descripcion']