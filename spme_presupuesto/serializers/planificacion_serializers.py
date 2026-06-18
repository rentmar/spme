#spme/spme_presupuesto/serializers/planificacion_serializers.py
from rest_framework import serializers

########### Serializadores de entidades relaciondas #####################
class FuentesAsociadasSerializer(serializers.Serializer):
    """
    Fuentes de financiamiento asociadas al proyecto (M2M)
    """
    sigla = serializers.CharField()
    financiera = serializers.CharField()

class InstanciaGestoraSerializer(serializers.Serializer):
    """
    Instancia gestora asociada al proyecto (M2M)
    """
    codigo = serializers.CharField()
    instancia = serializers.CharField()

########### Serializador de Tareas ############################
class PartidaTareaSerializer(serializers.Serializer):
    partida = serializers.CharField()
    descripcion = serializers.CharField()
    monto = serializers.DecimalField(max_digits=12, decimal_places=2)

class TareaPlanificadaSerializer(serializers.Serializer):
    codigo = serializers.CharField()
    titulo = serializers.CharField()
    presupuesto = serializers.DecimalField(max_digits=12, decimal_places=2)
    estado = serializers.CharField()
    partidas = PartidaTareaSerializer(many=True)
    suma_partidas = serializers.DecimalField(max_digits=12, decimal_places=2)
    fecha_limite = serializers.DateField()

########### Serializador de Actividades ############################
class ProcedenciaFondosItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    nombre = serializers.CharField()
    monto = serializers.DecimalField(max_digits=12, decimal_places=2)
    manual = serializers.BooleanField(required=False, default=False)

class ActividadPlanificadaSerializer(serializers.Serializer):
    codigo = serializers.CharField()
    nombre = serializers.CharField()
    estado = serializers.CharField()
    tipo = serializers.CharField(required=False, allow_null=True)
    presupuesto = serializers.DecimalField(max_digits=12, decimal_places=2)
    procedencia_fondos = ProcedenciaFondosItemSerializer(many=True)
    suma_fuentes = serializers.DecimalField(max_digits=12, decimal_places=2)
    num_tareas = serializers.IntegerField()
    tareas = TareaPlanificadaSerializer(many=True, required=False)
    fecha_programada = serializers.DateField(required=False, allow_null=True)

########### Serializador de Proyecto ############################
class ProyectoPlanificacionSerializer(serializers.Serializer):
    """
    Resumen de planificacion del proyecto
    """
    proyecto_codigo = serializers.CharField()
    proyecto_titulo = serializers.CharField()
    proyecto_estado = serializers.CharField()
    presupuesto_global = serializers.DecimalField(max_digits=15, decimal_places=2)
    fuentes_asociadas = FuentesAsociadasSerializer(many=True)
    instancias_gestoras = InstanciaGestoraSerializer(many=True)
    consolidado_por_fuentes = serializers.DictField()
    total_consolidado = serializers.DecimalField(max_digits=15, decimal_places=2)
    num_actividades = serializers.IntegerField()
    num_tareas = serializers.IntegerField()
    mensaje = serializers.CharField(required=False, allow_blank=True)


############# Serializadores de consolidado por Fuente ##################
class ConsolidadoFuenteItemSerializer(serializers.Serializer):
    """
    Una fuente en el consolidado
    """
    nombre = serializers.CharField()
    planificado_total = serializers.DecimalField(max_digits=15, decimal_places=2)
    porcentaje = serializers.FloatField()
    actividades = serializers.ListField()
    manual = serializers.BooleanField(required=False, default=False)

class ConsolidadoFuenteSerializer(serializers.Serializer):
    """
    Consolidado completo por fuente
    """
    fuentes = ConsolidadoFuenteItemSerializer(many=True)
    total_global = serializers.DecimalField(max_digits=15, decimal_places=2)

############# Serializadores validaciones ##################
class ValidacionActividadSerializer(serializers.Serializer):
    valido = serializers.BooleanField()
    actividad_codigo = serializers.CharField()
    presupuesto = serializers.DecimalField(max_digits=12, decimal_places=2)
    suma_fuentes = serializers.DecimalField(max_digits=12, decimal_places=2)
    diferencia = serializers.DecimalField(max_digits=12, decimal_places=2)
    mensaje = serializers.CharField()
    fuentes_detalle = ProcedenciaFondosItemSerializer(many=True, required=False)


class ValidacionProyectoSerializer(serializers.Serializer):
    valido = serializers.BooleanField()
    proyecto_codigo = serializers.CharField()
    presupuesto_proyecto = serializers.DecimalField(max_digits=15, decimal_places=2)
    suma_actividades = serializers.DecimalField(max_digits=15, decimal_places=2)
    diferencia = serializers.DecimalField(max_digits=15, decimal_places=2)
    num_actividades = serializers.IntegerField()
    mensaje = serializers.CharField()
    actividades_detalle = serializers.ListField(required=False)