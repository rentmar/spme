from rest_framework import serializers
from spme_estructuracion_pei.models import (
    Pei, 
    ObjetivoPei, 
    FactoresCriticos, 
    IndicadorPeiCuantitativo, 
    IndicadorPeiCualitativo
)

class FactoresCriticosSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactoresCriticos
        fields = '__all__'

class IndicadorPeiCuantitativoSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorPeiCuantitativo
        fields = '__all__'

class IndicadorPeiCualitativoSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorPeiCualitativo
        fields = '__all__'

class ObjetivoPeiSerializer(serializers.ModelSerializer):
    factores_criticos = FactoresCriticosSerializer(many=True, read_only=True)
    
    # Usar SerializerMethodField para obtener los indicadores específicos
    indicadores_cuantitativos = serializers.SerializerMethodField()
    indicadores_cualitativos = serializers.SerializerMethodField()
    
    class Meta:
        model = ObjetivoPei
        fields = [
            'id', 'codigo', 'descripcion', 
            'factores_criticos', 'indicadores_cuantitativos', 'indicadores_cualitativos'
        ]
    
    def get_indicadores_cuantitativos(self, obj):
        cuantitativos = IndicadorPeiCuantitativo.objects.filter(objetivo=obj)
        return IndicadorPeiCuantitativoSerializer(cuantitativos, many=True).data
    
    def get_indicadores_cualitativos(self, obj):
        cualitativos = IndicadorPeiCualitativo.objects.filter(objetivo=obj)
        return IndicadorPeiCualitativoSerializer(cualitativos, many=True).data

class ResumenEstructuraSerializer(serializers.Serializer):
    """Serializer para el resumen de totales"""
    total_objetivos = serializers.IntegerField()
    total_factores_criticos = serializers.IntegerField()
    total_indicadores_cuantitativos = serializers.IntegerField()
    total_indicadores_cualitativos = serializers.IntegerField()
    total_indicadores = serializers.SerializerMethodField()
    
    def get_total_indicadores(self, obj):
        return obj['total_indicadores_cuantitativos'] + obj['total_indicadores_cualitativos']

class PeiEstructuraSerializer(serializers.ModelSerializer):
    # Incluir todos los objetivos del PEI con su estructura completa
    objetivos = ObjetivoPeiSerializer(
        source='pei_obj_general', 
        many=True, 
        read_only=True
    )
    
    # Resumen de totales en un campo separado
    resumen = serializers.SerializerMethodField()
    
    class Meta:
        model = Pei
        fields = [
            'id', 'codigo', 'titulo', 'descripcion',
            'fecha_creacion', 'fecha_inicio', 'fecha_fin',
            'esta_vigente', 'creado_el', 'modificado_el',
            'objetivos', 'resumen'
        ]
    
    def get_resumen(self, obj):
        # Calcular todos los totales
        total_objetivos = obj.pei_obj_general.count()
        
        total_factores_criticos = FactoresCriticos.objects.filter(
            objetivo_especifico__in=obj.pei_obj_general.all()
        ).count()
        
        total_indicadores_cuantitativos = IndicadorPeiCuantitativo.objects.filter(
            objetivo__in=obj.pei_obj_general.all()
        ).count()
        
        total_indicadores_cualitativos = IndicadorPeiCualitativo.objects.filter(
            objetivo__in=obj.pei_obj_general.all()
        ).count()
        
        # Crear el objeto de resumen
        resumen_data = {
            'total_objetivos': total_objetivos,
            'total_factores_criticos': total_factores_criticos,
            'total_indicadores_cuantitativos': total_indicadores_cuantitativos,
            'total_indicadores_cualitativos': total_indicadores_cualitativos,
        }
        
        return ResumenEstructuraSerializer(resumen_data).data