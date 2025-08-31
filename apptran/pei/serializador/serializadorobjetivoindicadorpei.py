from rest_framework import serializers
from spme_estructuracion_pei.models import *

class ObjetivoPeiSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjetivoPei
        fields = ['id', 'codigo', 'descripcion', 'pei', 'creado_el', 'modificado_el']


class ObjetivoPeiSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjetivoPei
        fields = ['id', 'codigo', 'descripcion', 'pei', 'creado_el', 'modificado_el']



class IndicadorPeiBaseSerializer(serializers.ModelSerializer):
    tipo_indicador = serializers.SerializerMethodField()
    
    class Meta:
        model = IndicadorPeiBase
        fields = [
            'id', 'codigo', 'descripcion', 'captura_informacion', 
            'responsabilidad', 'frecuencia_recopilacion', 'uso_informacion',
            'objetivo', 'creado_el', 'modificado_el', 'tipo_indicador'
        ]
    
    def get_tipo_indicador(self, obj):
        if hasattr(obj, 'indicadorpeicuantitativo'):
            return 'cuantitativo'
        elif hasattr(obj, 'indicadorpeicualitativo'):
            return 'cualitativo'
        return 'base'

# Serializer polimórfico para manejar ambos tipos de indicadores
class IndicadorPeiSerializer(serializers.ModelSerializer):
    tipo = serializers.SerializerMethodField()
    detalles = serializers.SerializerMethodField()
    
    class Meta:
        model = IndicadorPeiBase
        fields = [
            'id', 'codigo', 'descripcion', 'captura_informacion', 
            'responsabilidad', 'frecuencia_recopilacion', 'uso_informacion',
            'objetivo', 'creado_el', 'modificado_el', 'tipo', 'detalles'
        ]
    
    def get_tipo(self, obj):
        # Obtener la instancia real del modelo polimórfico
        real_instance = obj.get_real_instance()
        
        if isinstance(real_instance, IndicadorPeiCuantitativo):
            return 'cuantitativo'
        elif isinstance(real_instance, IndicadorPeiCualitativo):
            return 'cualitativo'
        return 'base'
    
    def get_detalles(self, obj):
        # Obtener la instancia real del modelo polimórfico
        real_instance = obj.get_real_instance()
        
        if isinstance(real_instance, IndicadorPeiCuantitativo):
            return {
                'numerador': real_instance.numerador,
                'denominador': real_instance.denominador,
                'umbral_des_numeral': real_instance.umbral_des_numeral,
                'umbral_des_literal_um1': real_instance.umbral_des_literal_um1,
                'umbral_des_literal_um2': real_instance.umbral_des_literal_um2,
                'umbral_des_literal_um3': real_instance.umbral_des_literal_um3,
            }
        elif isinstance(real_instance, IndicadorPeiCualitativo):
            return {
                'umbral_des_literal_um1': real_instance.umbral_des_literal_um1,
                'umbral_des_literal_um2': real_instance.umbral_des_literal_um2,
                'umbral_des_literal_um3': real_instance.umbral_des_literal_um3,
            }
        return {}