from rest_framework import serializers

class ObtenerActividadesUsuarioRequest(serializers.Serializer):
    user_id = serializers.IntegerField()

    def to_internal_value(self, data):
        """
        Convierte los campos a un formato interno.
        """
        internal_value = super().to_internal_value(data)
        return {
            'user_id': int(internal_value['user_id']),
        }
    
class CrearActividadRequest(serializers.Serializer):
    codigo = serializers.CharField(max_length=60)
    nombre_corto = serializers.CharField(max_length=500)
    descripcion = serializers.CharField(max_length=500)
    supuestos = serializers.CharField(max_length = 500)
    riesgos = serializers.CharField(max_length = 500)
    objetivo_de_actividad = serializers.CharField(max_length=500)
    descripcion_evaluacion = serializers.CharField(max_length=500)
    fecha_programada = serializers.DateField()
    fecha_inicio = serializers.DateField()
    fecha_cierre = serializers.DateField()
    presupuesto = serializers.DecimalField(max_digits=6, decimal_places=2)
    presupuesto_global = serializers.DecimalField(max_digits=6, decimal_places=2)
    procedencia_fondos = serializers.JSONField()
    estado = serializers.CharField(max_length=15)
    indicador_pei_id = serializers.IntegerField(allow_null=True)
    objetivo_pei_id = serializers.IntegerField(allow_null=True)
    proceso_id = serializers.IntegerField(allow_null=True)
    producto_oe_id = serializers.IntegerField(allow_null=True)
    proyecto_id = serializers.IntegerField(allow_null=True)
    responsable_id = serializers.IntegerField(allow_null=True)
    resultado_oe_id = serializers.IntegerField(allow_null=True)
    resultado_og_id = serializers.IntegerField(allow_null=True)
    
    def to_internal_value(self, data):
        """
        Convierte los campos a un formato interno.
        """
        internal_value = super().to_internal_value(data)
        return {
            'codigo': internal_value['codigo'],
            'nombreCorto': internal_value['nombre_corto'],
            'descripcion': internal_value['descripcion'],
            'supuestos': internal_value['supuestos'],
            'riesgos': internal_value['riesgos'],
            'objetivo_de_actividad': internal_value['objetivo_de_actividad'],
            'descripcion_evaluacion': internal_value['descripcion_evaluacion'],
            'fecha_programada': internal_value['fecha_programada'],
            'fecha_inicio': internal_value['fecha_inicio'],
            'fecha_cierre': internal_value['fecha_cierre'],
            'presupuesto': internal_value['presupuesto'],
            'presupuestoGlobal': internal_value['presupuesto_global'],
            'procedencia_fondos': internal_value['procedencia_fondos'],
            'estado' : internal_value['estado'],
            'indicador_pei_id' :internal_value['indicador_pei_id'],
            'objetivo_pei_id': internal_value['objetivo_pei_id'],
            'proceso_id': internal_value['proceso_id'],
            'producto_oe_id': internal_value['producto_oe_id'],
            'proyecto_id': internal_value['proyecto_id'],
            'responsable_id': internal_value['responsable_id'],
            'resultado_oe_id': internal_value['resultado_oe_id'],
            'resultado_og_id': internal_value['resultado_og_id'],
        }
    
class ObtenerActividadIdRequest(serializers.Serializer):
    actividad_id = serializers.IntegerField()

    def to_internal_value(self, data):
        """
        Convierte los campos a un formato interno.
        """
        internal_value = super().to_internal_value(data)
        return {
            'id': int(internal_value['actividad_id']),
        }

class ObtenerDatosFormActividadPorIdRequest(serializers.Serializer):
    actividad_id = serializers.IntegerField()

    def to_internal_value(self, data):
        """
        Convierte los campos a un formato interno.
        """
        internal_value = super().to_internal_value(data)
        return {
            'id': int(internal_value['actividad_id']),
        }

class ObtenerEncabezadoPorIdRequest(serializers.Serializer):
    actividad_id = serializers.IntegerField()

    def to_internal_value(self, data):
        """
        Convierte los campos a un formato interno.
        """
        internal_value = super().to_internal_value(data)
        return {
            'id': int(internal_value['actividad_id']),
        }