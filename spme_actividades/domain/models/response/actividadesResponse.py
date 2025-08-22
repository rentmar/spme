from rest_framework import serializers

class ActividadeKantResponse(serializers.Serializer):
    codigo = serializers.CharField(max_length=60)
    descripcion = serializers.CharField(max_length=500)
    tipo = serializers.CharField(max_length=30)
    fecha_programada = serializers.DateField()
    duracion = serializers.IntegerField()
    fecha_inicio = serializers.DateField()
    fecha_cierre = serializers.DateField()
    estado = serializers.CharField(max_length=15)

class ActividadResponse(ActividadeKantResponse):
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

class ActividadesKantResponse(serializers.Serializer):
    actividades = ActividadeKantResponse(many=True)

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
    fecha_programada = serializers.DateField(required=False)
    fecha_inicio = serializers.DateField(required=False)
    fecha_cierre = serializers.DateField(required=False)
    presupuesto = serializers.DecimalField(max_digits=6, decimal_places=2, required=False)
    presupuesto_global = serializers.DecimalField(max_digits=6, decimal_places=2, required=False)
    procedencia_fondos = serializers.CharField(max_length=100, required=False)
    estado = serializers.CharField(max_length=15, required=False)
    responsable = serializers.CharField(max_length=100, required=False)
    objetivo_pei = serializers.IntegerField(required=False)
    indicador_pei = serializers.IntegerField(required=False)
    proceso_id = serializers.IntegerField(required=False)
    producto_oe_id = serializers.IntegerField(required=False)
    resultado_oe_id = serializers.IntegerField(required=False)
    resultado_og_id = serializers.IntegerField(required=False)

class ObtenerDatosFormActividadResponse(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    descripcion = serializers.CharField(max_length=100, required=False)
    fecha_inicio = serializers.DateField(required=False)
    fecha_cierre = serializers.DateField(required=False)
    objetivo_de_actividad = serializers.CharField(max_length=100, required=False)

class ObtenerEncabezadoActividadResponse(serializers.Serializer):
    codigo = serializers.CharField(max_length=60, required=False)
    descripcion = serializers.CharField(max_length=500, required=False)
    estado = serializers.CharField(max_length=15, required=False)
    tipo = serializers.CharField(max_length=100, required=False)
    fecha_programada = serializers.DateField(required=False)
    fecha_cierre = serializers.DateField(required=False)
    presupuesto = serializers.DecimalField(max_digits=6, decimal_places=2, required=False)
    responsable = serializers.JSONField(required=False)
