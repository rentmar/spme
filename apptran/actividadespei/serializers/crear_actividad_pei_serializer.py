from rest_framework import serializers
from spme_estructuracion_pei.models import (
    ActividadPei,
    ObjetivoPei,
    IndicadorPeiCuantitativo,
    IndicadorPeiCualitativo
)

class ActividadPeiSerializer(serializers.ModelSerializer):
    # Campos para las relaciones ManyToMany (write-only)
    objetivos_pei_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    factores_criticos_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    indicadores_cuantitativos_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    indicadores_cualitativos_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    
    # Campos de solo lectura para mostrar información relacionada
    objetivos_pei_info = serializers.SerializerMethodField(read_only=True)
    factores_criticos_info = serializers.SerializerMethodField(read_only=True)
    indicadores_cuantitativos_info = serializers.SerializerMethodField(read_only=True)
    indicadores_cualitativos_info = serializers.SerializerMethodField(read_only=True)
    responsable_info = serializers.SerializerMethodField(read_only=True)
    tipo_info = serializers.SerializerMethodField(read_only=True)
    pei_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ActividadPei
        fields = [
            'id', 'codigo', 'nombreCorto', 'descripcion', 'supuestos', 'riesgos',
            'objetivo_de_actividad', 'descripcion_evaluacion', 'descripcion_tipo_actividad',
            'tipo', 'tipo_info', 'fecha_programada', 'fecha_inicio', 'fecha_cierre',
            'presupuesto', 'presupuestoGlobal', 'totalReportado', 'totalEjecutado', 'saldo',
            'gradoEjecucion', 'procedencia_fondos', 'estado', 'pei', 'pei_info',
            'responsable', 'responsable_info', 
            'objetivos_pei_ids', 'factores_criticos_ids', 
            'indicadores_cuantitativos_ids', 'indicadores_cualitativos_ids',
            'objetivos_pei_info', 'factores_criticos_info',
            'indicadores_cuantitativos_info', 'indicadores_cualitativos_info'
        ]
        extra_kwargs = {
            'procedencia_fondos': {'required': False, 'allow_null': True},
            'codigo': {'required': False, 'allow_null': True},
            'nombreCorto': {'required': False, 'allow_null': True},
        }

    def get_objetivos_pei_info(self, obj):
        return [{'id': objetivo.id, 'codigo': objetivo.codigo, 'descripcion': objetivo.descripcion} 
                for objetivo in obj.objetivos_pei.all()]

    def get_factores_criticos_info(self, obj):
        return [{'id': factor.id, 'factor_critico': factor.factor_critico} 
                for factor in obj.factores_criticos.all()]

    def get_indicadores_cuantitativos_info(self, obj):
        return [{'id': ind.id, 'codigo': ind.codigo, 'descripcion': ind.descripcion} 
                for ind in obj.indicadores_cuantitativos.all()]

    def get_indicadores_cualitativos_info(self, obj):
        return [{'id': ind.id, 'codigo': ind.codigo, 'descripcion': ind.descripcion} 
                for ind in obj.indicadores_cualitativos.all()]

    def get_responsable_info(self, obj):
        if obj.responsable:
            return {
                'id': obj.responsable.id,
                'username': obj.responsable.username,
                'nombre_completo': obj.responsable.get_full_name(),
                'nombre': obj.responsable.nombre,
                'paterno': obj.responsable.paterno,
                'materno': obj.responsable.materno,
                'ci': obj.responsable.ci,
                'cargo': obj.responsable.cargo,
                'is_active': obj.responsable.is_active
            }
        return None

    def get_tipo_info(self, obj):
        if obj.tipo:
            return {
                'id': obj.tipo.id,
                'sigla': obj.tipo.sigla,
                'tipo_actividad': obj.tipo.tipo_actividad
            }
        return None

    def get_pei_info(self, obj):
        if obj.pei:
            return {
                'id': obj.pei.id,
                'codigo': obj.pei.codigo,
                'titulo': obj.pei.titulo
            }
        return None

    def validate_procedencia_fondos(self, value):
        if value is not None and not isinstance(value, (dict, list)):
            raise serializers.ValidationError("procedencia_fondos debe ser un objeto JSON válido")
        return value

    def create(self, validated_data):
        objetivos_pei_ids = validated_data.pop('objetivos_pei_ids', [])
        factores_criticos_ids = validated_data.pop('factores_criticos_ids', [])
        indicadores_cuantitativos_ids = validated_data.pop('indicadores_cuantitativos_ids', [])
        indicadores_cualitativos_ids = validated_data.pop('indicadores_cualitativos_ids', [])
        
        actividad = ActividadPei.objects.create(**validated_data)
        
        if objetivos_pei_ids:
            actividad.objetivos_pei.set(objetivos_pei_ids)
        if factores_criticos_ids:
            actividad.factores_criticos.set(factores_criticos_ids)
        if indicadores_cuantitativos_ids:
            actividad.indicadores_cuantitativos.set(indicadores_cuantitativos_ids)
        if indicadores_cualitativos_ids:
            actividad.indicadores_cualitativos.set(indicadores_cualitativos_ids)
        
        return actividad

    def update(self, instance, validated_data):
        objetivos_pei_ids = validated_data.pop('objetivos_pei_ids', None)
        factores_criticos_ids = validated_data.pop('factores_criticos_ids', None)
        indicadores_cuantitativos_ids = validated_data.pop('indicadores_cuantitativos_ids', None)
        indicadores_cualitativos_ids = validated_data.pop('indicadores_cualitativos_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if objetivos_pei_ids is not None:
            instance.objetivos_pei.set(objetivos_pei_ids)
        if factores_criticos_ids is not None:
            instance.factores_criticos.set(factores_criticos_ids)
        if indicadores_cuantitativos_ids is not None:
            instance.indicadores_cuantitativos.set(indicadores_cuantitativos_ids)
        if indicadores_cualitativos_ids is not None:
            instance.indicadores_cualitativos.set(indicadores_cualitativos_ids)
        
        return instance