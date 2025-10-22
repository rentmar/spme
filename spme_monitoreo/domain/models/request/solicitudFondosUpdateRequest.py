from rest_framework import serializers

class ActualizarValidacionSolicitudFondosRequest(serializers.Serializer):
    """
    Request para actualizar validaciones de una Solicitud de Fondos.
    """
    id_solicitud = serializers.IntegerField(required=True, allow_null=False)
    validacion_responsable = serializers.BooleanField(required=False, allow_null=True)
    validacion_coordinador = serializers.BooleanField(required=False, allow_null=True)
    
    def validate(self, data):
        """
        Valida que al menos una validación sea proporcionada.
        """
        if 'validacion_responsable' not in data and 'validacion_coordinador' not in data:
            raise serializers.ValidationError(
                "Debe proporcionar al menos una validación a actualizar (validacion_responsable o validacion_coordinador)"
            )
        return data
    
    def to_internal_value(self, data):
        """
        Convierte los campos a un formato interno.
        """
        internal_value = super().to_internal_value(data)
        return {
            'solicitud_id': int(internal_value['id_solicitud']),
            'validacion_responsable': internal_value.get('validacion_responsable'),
            'validacion_coordinador': internal_value.get('validacion_coordinador')
        }