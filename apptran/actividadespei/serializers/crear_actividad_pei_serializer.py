# serializers.py
from rest_framework import serializers
from spme_estructuracion_pei.models import ActividadPei, ObjetivoPei, FactoresCriticos, IndicadorPeiCuantitativo, IndicadorPeiCualitativo

class ActividadPeiSerializer(serializers.ModelSerializer):
    # Sobrescribir campos ManyToMany para permitir listas vacías
    objetivos_pei = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ObjetivoPei.objects.all(),
        required=False,
        allow_empty=True
    )
    
    factores_criticos = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=FactoresCriticos.objects.all(),
        required=False,
        allow_empty=True
    )
    
    indicadores_cuantitativos = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=IndicadorPeiCuantitativo.objects.all(),
        required=False,
        allow_empty=True
    )
    
    indicadores_cualitativos = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=IndicadorPeiCualitativo.objects.all(),
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = ActividadPei
        fields = '__all__'
        extra_kwargs = {
            'objetivos_pei': {'allow_empty': True, 'required': False},
            'factores_criticos': {'allow_empty': True, 'required': False},
            'indicadores_cuantitativos': {'allow_empty': True, 'required': False},
            'indicadores_cualitativos': {'allow_empty': True, 'required': False},
        }
    
    def create(self, validated_data):
        """
        Crear una nueva actividad PEI
        """
        # Extraer los datos de las relaciones
        objetivos_pei = validated_data.pop('objetivos_pei', [])
        factores_criticos = validated_data.pop('factores_criticos', [])
        indicadores_cuantitativos = validated_data.pop('indicadores_cuantitativos', [])
        indicadores_cualitativos = validated_data.pop('indicadores_cualitativos', [])
        
        # Crear la instancia principal
        instance = super().create(validated_data)
        
        # Establecer las relaciones
        instance.objetivos_pei.set(objetivos_pei)
        instance.factores_criticos.set(factores_criticos)
        instance.indicadores_cuantitativos.set(indicadores_cuantitativos)
        instance.indicadores_cualitativos.set(indicadores_cualitativos)
        
        return instance
    
    def update(self, instance, validated_data):
        """
        Actualizar una actividad PEI existente
        """
        # Extraer los datos de las relaciones
        objetivos_pei = validated_data.pop('objetivos_pei', None)
        factores_criticos = validated_data.pop('factores_criticos', None)
        indicadores_cuantitativos = validated_data.pop('indicadores_cuantitativos', None)
        indicadores_cualitativos = validated_data.pop('indicadores_cualitativos', None)
        
        # Actualizar la instancia principal
        instance = super().update(instance, validated_data)
        
        # Actualizar las relaciones si se proporcionan
        if objetivos_pei is not None:
            instance.objetivos_pei.set(objetivos_pei)
        if factores_criticos is not None:
            instance.factores_criticos.set(factores_criticos)
        if indicadores_cuantitativos is not None:
            instance.indicadores_cuantitativos.set(indicadores_cuantitativos)
        if indicadores_cualitativos is not None:
            instance.indicadores_cualitativos.set(indicadores_cualitativos)
        
        return instance