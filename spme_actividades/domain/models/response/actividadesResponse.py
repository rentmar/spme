from rest_framework import serializers

class ActividadGanttResponse(serializers.Serializer):
    nombre_responsable = serializers.CharField(max_length=150,allow_null=True)
    codigo = serializers.CharField(max_length=60,allow_null=True)
    nombre_corto = serializers.CharField(max_length=100,allow_null=True)
    descripcion = serializers.CharField(max_length=500,allow_null=True)
    tipo = serializers.CharField(max_length=30,allow_null=True)
    fecha_programada = serializers.DateField(allow_null=True)
    fecha_inicio = serializers.DateField(allow_null=True)
    fecha_cierre = serializers.DateField(allow_null=True)
    grado_ejecucion = serializers.CharField(max_length=25,allow_null=True)
    estado = serializers.CharField(max_length=15,allow_null=True)

class EstadoActividadResponse(serializers.Serializer):
    id = serializers.CharField(max_length=9,allow_null=True)
    nombre = serializers.CharField(max_length=100,allow_null=True)
    color = serializers.CharField(max_length=7,allow_null=True)

class ActividadResponse(ActividadGanttResponse):
    id = serializers.IntegerField()
    presupuesto = serializers.DecimalField(max_digits=10, decimal_places=2)
    presupuesto_pei = serializers.DecimalField(max_digits=10, decimal_places=2)
    procedencia_fondos = serializers.CharField(max_length=25)
    objetivo_de_actividad = serializers.CharField(max_length=500)
    descripcion_evaluacion = serializers.CharField(max_length=500)
    justificacion_modificacion = serializers.CharField(max_length=500)
    datos_actividad = serializers.JSONField()

class ActividadesUsuarioResponse(serializers.Serializer):
    actividades = ActividadResponse(many=True)

class ActividadesGanttResponse(serializers.Serializer):
    estados = EstadoActividadResponse(many=True)
    actividades = ActividadGanttResponse(many=True)

class CrearActividadResponse(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    mensaje = serializers.CharField(required=False, allow_blank=True, max_length=150)

class ObtenerActividadIdResponse(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    codigo = serializers.CharField(max_length=60, required=False)
    descripcion = serializers.CharField(max_length=500, required=False)
    supuestos = serializers.CharField(max_length=500, required=False)
    riesgos = serializers.CharField(max_length=500, required=False)
    objetivo_de_actividad = serializers.CharField(max_length=350, required=False)
    descripcion_evaluacion = serializers.CharField(max_length=500, required=False)
    fecha_programada = serializers.DateField(required=False,allow_null=True)
    fecha_inicio = serializers.DateField(required=False,allow_null=True)
    fecha_cierre = serializers.DateField(required=False,allow_null=True)
    presupuesto = serializers.DecimalField(max_digits=12, decimal_places=2, required=False,allow_null=True)
    presupuesto_global = serializers.DecimalField(max_digits=12, decimal_places=2, required=False,allow_null=True)
    procedencia_fondos = serializers.CharField(max_length=100, required=False,allow_null=True)
    estado = serializers.CharField(max_length=15, required=False)
    responsable = serializers.CharField(max_length=100, required=False)
    objetivo_pei = serializers.IntegerField(required=False)
    indicador_pei = serializers.IntegerField(required=False)
    proceso_id = serializers.IntegerField(required=False)
    producto_oe_id = serializers.IntegerField(required=False)
    resultado_oe_id = serializers.IntegerField(required=False)
    resultado_og_id = serializers.IntegerField(required=False)

class ObtenerEncabezadoActividadResponse(serializers.Serializer):
    codigo = serializers.CharField(max_length=60, required=False,allow_null=True)
    descripcion = serializers.CharField(max_length=500, required=False, allow_null=True)
    estado = serializers.CharField(max_length=15, required=False,allow_null=True)
    tipo = serializers.CharField(max_length=100, required=False,allow_null=True)
    fecha_programada = serializers.DateField(required=False, allow_null=True)
    fecha_cierre = serializers.DateField(required=False,allow_null=True)
    presupuesto = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    responsable = serializers.CharField(max_length=150, required=False,allow_null=True)
