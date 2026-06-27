# spme/spme_presupuesto/serializers/balance_serializers.py
from rest_framework import serializers

################ Serializadores Ejecucion #####################

class SolicitudEjecutadaSerializer(serializers.Serializer):
    tipo = serializers.CharField()
    numero = serializers.CharField()
    monto = serializers.DecimalField(max_digits=12, decimal_places=2)
    fecha = serializers.DateField(required=False, allow_null=True)
    tarea_id = serializers.IntegerField(required=False, allow_null=True)
    es_directa = serializers.BooleanField(required=False)


class TareaEjecutadaSerializer(serializers.Serializer):
    tarea_id = serializers.IntegerField()
    tarea_codigo = serializers.CharField()
    tarea_titulo = serializers.CharField()
    ejecutado = serializers.DecimalField(max_digits=12, decimal_places=2)
    solicitudes = SolicitudEjecutadaSerializer(many=True)

class ActividadEjecutadaSerializer(serializers.Serializer):
    actividad_id = serializers.IntegerField()
    actividad_codigo = serializers.CharField()
    actividad_nombre = serializers.CharField()
    presupuesto = serializers.DecimalField(max_digits=12, decimal_places=2)
    ejecutado = serializers.DecimalField(max_digits=12, decimal_places=2)
    solicitudes_directas = SolicitudEjecutadaSerializer(many=True)
    tareas = TareaEjecutadaSerializer(many=True)
    total_ejecutado = serializers.DecimalField(max_digits=12, decimal_places=2)
    saldo = serializers.DecimalField(max_digits=12, decimal_places=2)
    porcentaje_ejecucion = serializers.CharField()

class TareaEjecucionDetalleSerializer(serializers.Serializer):
    tarea_id = serializers.IntegerField()
    tarea_codigo = serializers.CharField()
    tarea_titulo = serializers.CharField()
    presupuesto = serializers.DecimalField(max_digits=12, decimal_places=2)
    ejecutado = serializers.DecimalField(max_digits=12, decimal_places=2)
    solicitudes = SolicitudEjecutadaSerializer(many=True)

############# Serializadores de Balance #################3

class BalanceActividadItemSerializer(serializers.Serializer):
    codigo = serializers.CharField()
    nombre = serializers.CharField()
    estado = serializers.CharField()
    planificado = serializers.DecimalField(max_digits=12, decimal_places=2)
    ejecutado = serializers.DecimalField(max_digits=12, decimal_places=2)
    diferencia = serializers.DecimalField(max_digits=12, decimal_places=2)
    porcentaje_desviacion = serializers.FloatField()
    grado_ejecucion = serializers.CharField()
    saldo = serializers.DecimalField(max_digits=12, decimal_places=2)
    num_tareas = serializers.IntegerField()
    tareas_completadas = serializers.IntegerField()

class BalanceProyectoSerializer(serializers.Serializer):
    proyecto_codigo = serializers.CharField()
    proyecto_titulo = serializers.CharField()
    proyecto_estado = serializers.CharField()
    proyecto_estado_display = serializers.CharField()
    presupuesto_proyecto = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_ejecutado = serializers.DecimalField(max_digits=15, decimal_places=2)
    saldo_global = serializers.DecimalField(max_digits=15, decimal_places=2)
    porcentaje_ejecucion_global = serializers.FloatField()
    actividades = BalanceActividadItemSerializer(many=True)
    deficit_superavit_caja = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    conciliacion = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    mensaje = serializers.CharField(required=False, allow_blank=True)
