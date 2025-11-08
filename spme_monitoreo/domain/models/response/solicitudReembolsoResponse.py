from rest_framework import serializers

class CreateSolicitudReembolsoResponse(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    numero_formulario = serializers.CharField(required=False, allow_blank=True, max_length=150)  # NUEVO CAMPO
    mensaje = serializers.CharField(required=False, allow_blank=True, max_length=150)
    objetivo_reposicion = serializers.CharField(required=False, allow_blank=True, allow_null=True)  

    def to_representation(self, instance):
        """
        Convierte los datos internos a formato de respuesta.
        """
        representation = super().to_representation(instance)
        
        # Si instance es un diccionario (viene del mapper)
        if isinstance(instance, dict):
            return {
                'id': instance.get('id'),
                'numero_formulario': instance.get('numero_formulario'),
                'objetivo_reposicion': instance.get('objetivo_reposicion'),
                'mensaje': instance.get('mensaje')
            }
        
        # Si instance es un objeto del modelo
        return representation

class ObtenerSolicitudReembolsoResponse(serializers.Serializer):
    """
    Response para obtener solicitudes de reembolso
    """
    estado = serializers.CharField(required=False, max_length=50)
    solicitudes = serializers.ListField(required=False, allow_null=True)
    mensaje = serializers.CharField(required=False, allow_blank=True, max_length=150)