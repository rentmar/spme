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
    descripcion = serializers.CharField(max_length=500)
    tipo = serializers.CharField(max_length=30)
    fecha_programada = serializers.DateField()
    duracion = serializers.IntegerField()
    fecha_inicio = serializers.DateField()
    fecha_cierre = serializers.DateField()
    presupuesto = serializers.DecimalField(max_digits=10, decimal_places=2)
    presupuesto_pei = serializers.DecimalField(max_digits=10, decimal_places=2)
    estado = serializers.CharField(max_length=15)
    procedencia_fondos = serializers.CharField(max_length=25)
    objetivo_de_actividad = serializers.CharField(max_length=500)
    descripcion_evaluacion = serializers.CharField(max_length=500)
    justificacion_modificacion = serializers.CharField(max_length=500)
    datos_actividad = serializers.JSONField()
    proceso = serializers.IntegerField()
    resultado_og = serializers.IntegerField()
    resultado_oe = serializers.IntegerField()
    producto_oe = serializers.IntegerField()

    def to_internal_value(self, data):
        """
        Convierte los campos a un formato interno.
        """
        internal_value = super().to_internal_value(data)
        return {
            'codigo': internal_value['codigo'],
            'descripcion': internal_value['descripcion'],
            'tipo': internal_value['tipo'],
            'fecha_programada': internal_value['fecha_programada'],
            'duracion': internal_value['duracion'],
            'fecha_inicio': internal_value['fecha_inicio'],
            'fecha_cierre': internal_value['fecha_cierre'],
            'presupuesto': internal_value['presupuesto'],
            'presupuesto_pei': internal_value['presupuesto_pei'],
            'procedencia_fondos': internal_value['procedencia_fondos'],
            'objetivo_de_actividad': internal_value['objetivo_de_actividad'],
            'descripcion_evaluacion': internal_value['descripcion_evaluacion'],
            'justificacion_modificacion': internal_value['justificacion_modificacion'],
            'datos_actividad': internal_value['datos_actividad'],
            'proceso': internal_value['proceso'],
            'resultado_og': internal_value['resultado_og'],
            'resultado_oe': internal_value['resultado_oe'],
            'producto_oe': internal_value['producto_oe'],
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