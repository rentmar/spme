from rest_framework import serializers
    
class CrearEstructuraPEIRequest(serializers.Serializer):
    """
    Request para crear un Estructura PEI.
    """
    titulo = serializers.CharField(max_length=100, required=True, allow_blank=False)
    descripcion = serializers.CharField(max_length=250, required=True, allow_blank=False)
    fecha_creacion = serializers.DateTimeField()
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField()
    esta_vigente = serializers.BooleanField()
    creado_el = serializers.DateTimeField()
    modificado_el = serializers.DateTimeField()

    def to_internal_value(self, data):
        """
        Convierte los campos a un formato DB.
        """
        internal_value = super().to_internal_value(data)
        return {
            'titulo': internal_value['titulo'],
            'descripcion': internal_value['descripcion'],
            'fecha_creacion': internal_value['fecha_creacion'],
            'fecha_inicio': internal_value['fecha_inicio'],
            'fecha_fin': internal_value['fecha_fin'],
            'esta_vigente': internal_value['esta_vigente'],
            'creado_el': internal_value['creado_el'],
            'modificado_el': internal_value['modificado_el']
        }