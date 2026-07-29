# spme/spme_planificacion/serializers/planificacion.py
from rest_framework import serializers

class FechaNullableField(serializers.DateField):
    """Acepta '', null, y fechas válidas."""
    def to_internal_value(self, value):
        if value == '' or value is None:
            return None
        return super().to_internal_value(value)

class ActividadActualizarSerializer(serializers.Serializer):
    """
    Valida y mapea datos de actividades a actualizar.
    Mapea tipo_actividad_id → tipo_id para coincidir con el modelo.
    Ignora campos extra: tipo_actividad (literal), responsable (nombre), esNueva, tareas.
    """
    id = serializers.IntegerField()

    # Texto
    codigo = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    nombreCorto = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    descripcion = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    estado = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    supuestos = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    riesgos = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    objetivo_de_actividad = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    descripcion_evaluacion = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    descripcion_tipo_actividad = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    gradoEjecucion = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    # FK
    tipo_id = serializers.IntegerField(required=False, allow_null=True)
    responsable_id = serializers.IntegerField(required=False, allow_null=True)
    proceso_id = serializers.IntegerField(required=False, allow_null=True)
    resultado_og_id = serializers.IntegerField(required=False, allow_null=True)
    resultado_oe_id = serializers.IntegerField(required=False, allow_null=True)
    producto_oe_id = serializers.IntegerField(required=False, allow_null=True)
    objetivo_pei_id = serializers.IntegerField(required=False, allow_null=True)
    indicador_pei_id = serializers.IntegerField(required=False, allow_null=True)
    proyecto_id = serializers.IntegerField(required=False, allow_null=True)

    # Fechas
    fecha_programada = FechaNullableField(required=False, allow_null=True)
    fecha_inicio = FechaNullableField(required=False, allow_null=True)
    fecha_cierre = FechaNullableField(required=False, allow_null=True)

    # Decimales
    presupuesto = serializers.DecimalField(required=False, max_digits=12, decimal_places=2, allow_null=True)
    presupuestoGlobal = serializers.DecimalField(required=False, max_digits=12, decimal_places=2, allow_null=True)
    totalReportado = serializers.DecimalField(required=False, max_digits=12, decimal_places=2, allow_null=True)
    totalEjecutado = serializers.DecimalField(required=False, max_digits=12, decimal_places=2, allow_null=True)
    saldo = serializers.DecimalField(required=False, max_digits=12, decimal_places=2, allow_null=True)

    # JSON
    procedencia_fondos = serializers.JSONField(required=False, allow_null=True)
    rutaTrazadoIndicadores = serializers.JSONField(required=False, allow_null=True)
    factoresCriticos = serializers.JSONField(required=False, allow_null=True)
    estructuraProcedencia = serializers.JSONField(required=False, allow_null=True)

    # Booleano
    estaInactiva = serializers.BooleanField(required=False)

    def to_internal_value(self, data):
        """Mapea tipo_actividad_id → tipo_id"""
        if 'tipo_actividad_id' in data:
            data = dict(data)
            data['tipo_id'] = data.pop('tipo_actividad_id')
        return super().to_internal_value(data)


class ActividadCrearSerializer(serializers.Serializer):
    """Valida datos para crear nuevas actividades."""
    id = serializers.IntegerField(required=False, allow_null=True) 
    codigo = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    nombreCorto = serializers.CharField(required=False, allow_null=True, allow_blank=True, default='')
    descripcion = serializers.CharField(required=False, allow_null=True, allow_blank=True, default='')
    estado = serializers.CharField(required=False, allow_null=True, allow_blank=True, default='CRD')
    supuestos = serializers.CharField(required=False, allow_null=True, allow_blank=True, default='')
    riesgos = serializers.CharField(required=False, allow_null=True, allow_blank=True, default='')
    objetivo_de_actividad = serializers.CharField(required=False, allow_null=True, allow_blank=True, default='')
    descripcion_evaluacion = serializers.CharField(required=False, allow_null=True, allow_blank=True, default='')
    descripcion_tipo_actividad = serializers.CharField(required=False, allow_null=True, allow_blank=True, default='')
    gradoEjecucion = serializers.CharField(required=False, allow_null=True, allow_blank=True, default='PLANIFICADA')
    tipo_id = serializers.IntegerField(required=False, allow_null=True)
    responsable_id = serializers.IntegerField(required=False, allow_null=True)
    proceso_id = serializers.IntegerField(required=False, allow_null=True)
    resultado_og_id = serializers.IntegerField(required=False, allow_null=True)
    resultado_oe_id = serializers.IntegerField(required=False, allow_null=True)
    producto_oe_id = serializers.IntegerField(required=False, allow_null=True)
    objetivo_pei_id = serializers.IntegerField(required=False, allow_null=True)
    indicador_pei_id = serializers.IntegerField(required=False, allow_null=True)
    fecha_programada = FechaNullableField(required=False, allow_null=True)
    fecha_inicio = FechaNullableField(required=False, allow_null=True)
    fecha_cierre = FechaNullableField(required=False, allow_null=True)
    presupuesto = serializers.DecimalField(required=False, max_digits=12, decimal_places=2, allow_null=True, default=0)
    presupuestoGlobal = serializers.DecimalField(required=False, max_digits=12, decimal_places=2, allow_null=True)
    totalReportado = serializers.DecimalField(required=False, max_digits=12, decimal_places=2, allow_null=True)
    totalEjecutado = serializers.DecimalField(required=False, max_digits=12, decimal_places=2, allow_null=True)
    saldo = serializers.DecimalField(required=False, max_digits=12, decimal_places=2, allow_null=True, default=0)
    procedencia_fondos = serializers.JSONField(required=False, allow_null=True, default=list)
    rutaTrazadoIndicadores = serializers.JSONField(required=False, allow_null=True)
    factoresCriticos = serializers.JSONField(required=False, allow_null=True)
    estructuraProcedencia = serializers.JSONField(required=False, allow_null=True)
    estaInactiva = serializers.BooleanField(required=False, default=False)

    def to_internal_value(self, data):
        if 'tipo_actividad_id' in data:
            data = dict(data)
            data['tipo_id'] = data.pop('tipo_actividad_id')
        return super().to_internal_value(data)


class TareaActualizarSerializer(serializers.Serializer):
    """Valida datos de tareas a actualizar."""
    id = serializers.IntegerField()
    codigo = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    titulo = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    descripcion = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    estado = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    fecha_ejecucion = FechaNullableField(required=False, allow_null=True)
    fecha_limite = FechaNullableField(required=False, allow_null=True)
    fecha_creacion = FechaNullableField(required=False, allow_null=True)
    presupuesto = serializers.DecimalField(required=False, max_digits=12, decimal_places=2, allow_null=True)
    presupuestoDesglose = serializers.JSONField(required=False, allow_null=True)
    actividad_id = serializers.IntegerField(required=False, allow_null=True)


class TareaCrearSerializer(serializers.Serializer):
    """Valida datos para crear nuevas tareas."""
    codigo = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    titulo = serializers.CharField(required=False, allow_null=True, allow_blank=True, default='')
    descripcion = serializers.CharField(required=False, allow_null=True, allow_blank=True, default='')
    estado = serializers.CharField(required=False, allow_null=True, allow_blank=True, default='PEN')
    fecha_ejecucion = FechaNullableField(required=False, allow_null=True)
    fecha_limite = FechaNullableField(required=False, allow_null=True)
    presupuesto = serializers.DecimalField(required=False, max_digits=12, decimal_places=2, allow_null=True, default=0)
    presupuestoDesglose = serializers.JSONField(required=False, allow_null=True)
    actividad_id = serializers.IntegerField(required=True)