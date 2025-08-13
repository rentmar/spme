from rest_framework import serializers
from spme_estructuracion_pei.models import *

#Serializador Model PEI
class PeiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pei
        fields = '__all__'

#Serializador Model Objetivo PEI
class ObjetivoPeiSerializaer(serializers.ModelSerializer):
    class Meta:
        model = ObjetivoPei
        fields = '__all__'        

#Serializador Model Factores criticos PEI
class FactoresCriticosSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactoresCriticos
        fields = '__all__'
#Serializador Indicador Cuantitativo PEI
class IndicadorPeiCuantitativoSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorPeiCuantitativo
        fields = '__all__'
        read_only_fields = ['creado_el', 'modificado_el', 'id', 'tipo']

#Serializador Indicador Cualitativo PEI
class IndicadorPeiCualitativoSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorPeiCualitativo
        fields = '__all__'
        read_only_fields = ['creado_el', 'modificado_el', 'id', 'tipo']

class IndicadorPeiBaseSerializer(serializers.ModelSerializer):
    tipo_detalle = serializers.SerializerMethodField()
    tipo = serializers.CharField(write_only=True, required=True)  

    class Meta:
        model = IndicadorPeiBase
        fields = '__all__'

    def get_tipo_detalle(self, obj):
        if isinstance(obj, IndicadorPeiCuantitativo):
            return IndicadorPeiCuantitativoSerializer(obj).data
        elif isinstance(obj, IndicadorPeiCualitativo):
            return IndicadorPeiCualitativoSerializer(obj).data
        return None
    
    def create(self, validated_data):
        tipo = validated_data.pop('tipo')
        
        if tipo == 'Proporcion':
            return IndicadorPeiCuantitativo.objects.create(**validated_data)
        elif tipo == 'Avance':
            return IndicadorPeiCualitativo.objects.create(**validated_data)
        else:
            raise serializers.ValidationError("Tipo de indicador no válido")

##################### SERIALIZADORES Objetivos - Indicadores      #############################

# Serializador base polimórfico para indicadores
class IndicadorPeiPolymorphicSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        if isinstance(instance, IndicadorPeiCuantitativo):
            return IndicadorPeiCuantitativoSerializer(instance, context=self.context).data
        elif isinstance(instance, IndicadorPeiCualitativo):
            return IndicadorPeiCualitativoSerializer(instance, context=self.context).data
        return super().to_representation(instance)
    
    class Meta:
        model = IndicadorPeiBase
        fields = '__all__'

# Serializador para objetivos con sus indicadores
class ObjetivoPeiSerializer(serializers.ModelSerializer):
    indicadores = serializers.SerializerMethodField()
    
    class Meta:
        model = ObjetivoPei
        fields = ['id', 'codigo', 'descripcion', 'creado_el', 'modificado_el', 'indicadores']
    
    def get_indicadores(self, obj):
        # Obtener todos los indicadores relacionados con este objetivo
        indicadores = obj.indicador_pei_objetivo.all()
        return IndicadorPeiPolymorphicSerializer(indicadores, many=True).data

# Serializador para el PEI con sus objetivos
class PeiObjetivosSerializer(serializers.ModelSerializer):
    objetivos = ObjetivoPeiSerializer(many=True, read_only=True, source='pei_obj_general')
    
    class Meta:
        model = Pei
        fields = ['id', 'titulo', 'objetivos']

