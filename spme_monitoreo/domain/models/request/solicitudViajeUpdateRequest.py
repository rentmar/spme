from rest_framework import serializers

class ActualizarValidacionSolicitudViajeRequest(serializers.Serializer):
    id_solicitud_viaje = serializers.IntegerField(required=True, allow_null=False)
    validacion_responsable = serializers.BooleanField(required=False, allow_null=True)
    validacion_coordinador = serializers.BooleanField(required=False, allow_null=True)

    def validate(self, data):
        validaciones = ['validacion_responsable', 'validacion_coordinador']
        if not any(field in data for field in validaciones):
            raise serializers.ValidationError(
                "Debe proporcionar al menos una validación a actualizar"
            )
        return data

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        return {
            'solicitud_viaje_id': int(internal_value['id_solicitud_viaje']),
            'validacion_responsable': internal_value.get('validacion_responsable'),
            'validacion_coordinador': internal_value.get('validacion_coordinador')
        }