# serializers.py
from rest_framework import serializers
from spme_monitoreo.models import InfActividad
from spme_proyectos_reportes.models import BitacoraIndicadorBase

class BitacoraIndicadorSerializer(serializers.ModelSerializer):
    tipo_indicador_display = serializers.CharField(source='get_tipo_indicador_display', read_only=True)
    tipo_dato_display = serializers.CharField(source='get_tipo_dato_display', read_only=True)
    valor = serializers.SerializerMethodField()
    
    class Meta:
        model = BitacoraIndicadorBase
        fields = [
            'id', 'tipo_indicador', 'tipo_indicador_display', 'tipo_dato', 'tipo_dato_display',
            'id_indicador', 'valor', 'fecha_registro', 'observaciones', 'archivos_adjuntos',
            'timestamp_registro', 'snapshot_indicador'
        ]

    def get_valor(self, obj):
        if obj.tipo_dato == 'A-Z':
            return obj.valor_literal
        elif obj.tipo_dato == '1-9':
            return float(obj.valor_numerico) if obj.valor_numerico else None
        elif obj.tipo_dato == '%':
            return float(obj.valor_porcentual) if obj.valor_porcentual else None
        return None

class InfActividadSerializer(serializers.ModelSerializer):
    bitacoras_indicadores_base = BitacoraIndicadorSerializer(many=True, read_only=True)
    actividad_info = serializers.SerializerMethodField()
    
    class Meta:
        model = InfActividad
        fields = [
            'id', 'numeroInforme', 'fecha_ejecucion', 'contribucion_proyecto',
            'avance_indicadores', 'informacion_cuantitativa', 'herramientas_evaluacion',
            'medios_verificacion', 'comentarios_recomendaciones', 'presupuesto_planificado',
            'presupuesto_ejecutado', 'objetivo_actividad', 'informe_objetivo_actividad',
            'tipo_actividad', 'reporte_tipo', 'procedencia_fondos', 'observaciones_presupuesto',
            'archivos_cuantitativos', 'herramientas_archivos', 'medios_archivos', 'actividad',
            'actividad_info', 'bitacoras_indicadores_base'
        ]

    def get_actividad_info(self, obj):
        if obj.actividad:
            return {
                'id': obj.actividad.id,
                'codigo': obj.actividad.codigo,
                'titulo': obj.actividad.nombreCorto
            }
        return None

class InformeActividadCreateSerializer(serializers.ModelSerializer):
    actividad_id = serializers.IntegerField(required=True)
    tipo_de_actividad = serializers.CharField(write_only=True)  # Campo temporal
    objetivo_de_actividad = serializers.CharField(write_only=True)  # Campo temporal
    informe_de_objetivo_de_actividad = serializers.CharField(write_only=True)  # Campo temporal
    descripcion_herramientas = serializers.CharField(write_only=True)  # Campo temporal
    
    class Meta:
        model = InfActividad
        fields = [
            'fecha_ejecucion', 'objetivo_actividad', 'informe_objetivo_actividad',
            'tipo_actividad', 'reporte_tipo', 'informacion_cuantitativa',
            'herramientas_evaluacion', 'medios_verificacion', 'comentarios_recomendaciones',
            'observaciones_presupuesto', 'actividad_id', 
            'tipo_de_actividad', 'objetivo_de_actividad', 'informe_de_objetivo_de_actividad', 'descripcion_herramientas'  # Campos temporales
        ]
        extra_kwargs = {
            'tipo_actividad': {'read_only': True},
            'objetivo_actividad': {'read_only': True},
            'informe_objetivo_actividad': {'read_only': True},
            'herramientas_evaluacion': {'read_only': True}
        }
    
    def validate_actividad_id(self, value):
        from django.apps import apps
        Actividad = apps.get_model('spme_actividades', 'Actividad')
        try:
            Actividad.objects.get(id=value)
            return value
        except Actividad.DoesNotExist:
            raise serializers.ValidationError(f"Actividad con ID {value} no existe")
    
    def create(self, validated_data):
        # Extraer los valores de los campos temporales y asignarlos a los campos del modelo
        tipo_de_actividad = validated_data.pop('tipo_de_actividad', None)
        objetivo_de_actividad = validated_data.pop('objetivo_de_actividad', None)
        informe_de_objetivo_de_actividad = validated_data.pop('informe_de_objetivo_de_actividad', None)
        descripcion_herramientas = validated_data.pop('descripcion_herramientas', None)
        
        # Asignar los valores a los campos del modelo
        if tipo_de_actividad:
            validated_data['tipo_actividad'] = tipo_de_actividad
        if objetivo_de_actividad:
            validated_data['objetivo_actividad'] = objetivo_de_actividad
        if informe_de_objetivo_de_actividad:
            validated_data['informe_objetivo_actividad'] = informe_de_objetivo_de_actividad
        if descripcion_herramientas:
            validated_data['herramientas_evaluacion'] = descripcion_herramientas
        
        return super().create(validated_data)
    
    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        
        campos_adicionales = [
            'contribucion_actividad', 'avance_en_indicador', 'procedencia_fondos',
            'archivos_cuantitativos', 'herramientas_archivos', 'medios_archivos',
            'total_planificado', 'total_ejecutado', 'diferencia_total', 
            'porcentaje_ejecucion', 'timestamp'
        ]
        
        for campo in campos_adicionales:
            if campo in data:
                internal_value[campo] = data[campo]
        
        return internal_value