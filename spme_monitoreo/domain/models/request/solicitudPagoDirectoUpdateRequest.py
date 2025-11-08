from rest_framework import serializers

class ActualizarValidacionSolicitudPagoDirectoRequest(serializers.Serializer):
    """
    Request para actualizar validaciones de una Solicitud de Pago Directo.
    """
    
    id_solicitud = serializers.IntegerField(required=True, allow_null=False)
    validacion_responsable = serializers.BooleanField(required=False, allow_null=True)
    validacion_coordinador = serializers.BooleanField(required=False, allow_null=True)
    
    def validate(self, data):
        """
        Valida que al menos una validación sea proporcionada.
        """
        validaciones = ['validacion_responsable', 'validacion_coordinador']
        
        if not any(field in data for field in validaciones):
            raise serializers.ValidationError(
                "Debe proporcionar al menos una validación a actualizar"
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