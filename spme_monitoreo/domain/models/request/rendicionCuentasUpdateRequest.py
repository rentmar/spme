from rest_framework import serializers

class ActualizarValidacionRendicionCuentasRequest(serializers.Serializer):
    """
    Request para actualizar validaciones de una Rendición de Cuentas.
    """
    id_rendicion = serializers.IntegerField(required=True, allow_null=False)
    validacion_responsable = serializers.BooleanField(required=False, allow_null=True)
    validacion_coordinador = serializers.BooleanField(required=False, allow_null=True)
    validacion_contador = serializers.BooleanField(required=False, allow_null=True)
    validacion_administrador = serializers.BooleanField(required=False, allow_null=True)

    def validate(self, data):
        """
        Valida que al menos una validación sea proporcionada.
        """
        validaciones = ['validacion_responsable', 'validacion_coordinador', 'validacion_contador', 'validacion_administrador']
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
            'rendicion_id': int(internal_value['id_rendicion']),
            'validacion_responsable': internal_value.get('validacion_responsable'),
            'validacion_coordinador': internal_value.get('validacion_coordinador'),
            'validacion_contador': internal_value.get('validacion_contador'),
            'validacion_administrador': internal_value.get('validacion_administrador')
        }