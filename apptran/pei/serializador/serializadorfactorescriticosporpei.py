# serializers.py
from rest_framework import serializers
from spme_estructuracion_pei.models import FactoresCriticos, ObjetivoPei

class FactoresCriticosSerializer(serializers.ModelSerializer):
    codigo_objetivo_especifico = serializers.CharField(read_only=True)
    
    class Meta:
        model = FactoresCriticos
        fields = ['id', 'factor_critico', 'objetivo_especifico', 'codigo_objetivo_especifico']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Agregar el código del objetivo específico
        if instance.objetivo_especifico:
            representation['codigo_objetivo_especifico'] = instance.objetivo_especifico.codigo
        else:
            representation['codigo_objetivo_especifico'] = ""
        return representation