# serializers.py
from rest_framework import serializers
from spme_estructuracion_pei.models import ActividadPei, ObjetivoPei, FactoresCriticos, IndicadorPeiCuantitativo, IndicadorPeiCualitativo

class ObjetivoPeiRelacionSerializer(serializers.ModelSerializer):
    """Serializer para mostrar solo información básica de objetivos"""
    class Meta:
        model = ObjetivoPei
        fields = ['id', 'codigo', 'descripcion']

class FactoresCriticosRelacionSerializer(serializers.ModelSerializer):
    """Serializer para mostrar solo información básica de factores críticos"""
    class Meta:
        model = FactoresCriticos
        fields = ['id', 'factor_critico']

class IndicadorCuantitativoRelacionSerializer(serializers.ModelSerializer):
    """Serializer para mostrar solo información básica de indicadores cuantitativos"""
    class Meta:
        model = IndicadorPeiCuantitativo
        fields = ['id', 'codigo', 'descripcion', 'tipo']

class IndicadorCualitativoRelacionSerializer(serializers.ModelSerializer):
    """Serializer para mostrar solo información básica de indicadores cualitativos"""
    class Meta:
        model = IndicadorPeiCualitativo
        fields = ['id', 'codigo', 'descripcion', 'tipo']

class ActividadPeiListaPlanificacion(serializers.ModelSerializer):
    """
    Serializer específico para el endpoint actividades/pei/idpei/
    Devuelve el formato exacto solicitado para la planificacion
    """
    # Campo tipo como valor choice (sigla)
    tipo = serializers.SerializerMethodField()
    # Campo responsable como username (no ID)
    responsable = serializers.SerializerMethodField()
    pei = serializers.PrimaryKeyRelatedField(read_only=True)
    
    # Campos para las relaciones ManyToMany
    objetivos_pei = ObjetivoPeiRelacionSerializer(many=True, read_only=True)
    factores_criticos = FactoresCriticosRelacionSerializer(many=True, read_only=True)
    indicadores_cuantitativos = IndicadorCuantitativoRelacionSerializer(many=True, read_only=True)
    indicadores_cualitativos = IndicadorCualitativoRelacionSerializer(many=True, read_only=True)
    
    # Campos opcionales para IDs de relaciones (útil para crear/actualizar)
    objetivos_pei_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ObjetivoPei.objects.all(),
        source='objetivos_pei',
        write_only=True,
        required=False
    )
    
    factores_criticos_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=FactoresCriticos.objects.all(),
        source='factores_criticos',
        write_only=True,
        required=False
    )
    
    indicadores_cuantitativos_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=IndicadorPeiCuantitativo.objects.all(),
        source='indicadores_cuantitativos',
        write_only=True,
        required=False
    )
    
    indicadores_cualitativos_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=IndicadorPeiCualitativo.objects.all(),
        source='indicadores_cualitativos',
        write_only=True,
        required=False
    )

    class Meta:
        model = ActividadPei
        fields = [
            'id', 'codigo', 'nombreCorto', 'descripcion', 
            'supuestos', 'riesgos', 'objetivo_de_actividad',
            'descripcion_evaluacion', 'descripcion_tipo_actividad',
            'fecha_programada', 'fecha_inicio', 'fecha_cierre',
            'presupuesto', 'presupuestoGlobal', 'totalReportado', 
            'totalEjecutado', 'saldo', 'gradoEjecucion', 'procedencia_fondos',
            'estado', 'estaInactiva', 'tipo', 'pei', 'responsable',
            
            # Campos de relaciones (solo lectura)
            'objetivos_pei',
            'factores_criticos',
            'indicadores_cuantitativos',
            'indicadores_cualitativos',
            
            # Campos de IDs para escritura
            'objetivos_pei_ids',
            'factores_criticos_ids',
            'indicadores_cuantitativos_ids',
            'indicadores_cualitativos_ids',
        ]
        
        # Configurar campos de solo lectura
        read_only_fields = [
            'id', 'codigo', 'nombreCorto', 'descripcion', 
            'supuestos', 'riesgos', 'objetivo_de_actividad',
            'descripcion_evaluacion', 'descripcion_tipo_actividad',
            'fecha_programada', 'fecha_inicio', 'fecha_cierre',
            'presupuesto', 'presupuestoGlobal', 'totalReportado', 
            'totalEjecutado', 'saldo', 'gradoEjecucion', 'procedencia_fondos',
            'estado', 'estaInactiva', 'tipo', 'pei', 'responsable',
            'objetivos_pei', 'factores_criticos', 
            'indicadores_cuantitativos', 'indicadores_cualitativos'
        ]

    def get_tipo(self, obj):
        """
        Devuelve la sigla del tipo de actividad.
        """
        if obj.tipo:
            return obj.tipo.sigla if obj.tipo.sigla else "OTRO"
        return "NODEF"
    
    def get_responsable(self, obj):
        """
        Devuelve el username del responsable o null.
        """
        if obj.responsable:
            return obj.responsable.username
        return None
    
    def to_representation(self, instance):
        """
        Personalizar la representación de los datos.
        Puedes agregar lógica adicional aquí si es necesario.
        """
        representation = super().to_representation(instance)
        
        # Si no hay datos en las relaciones, devolver listas vacías
        for field in ['objetivos_pei', 'factores_criticos', 
                     'indicadores_cuantitativos', 'indicadores_cualitativos']:
            if representation[field] is None:
                representation[field] = []
                
        return representation