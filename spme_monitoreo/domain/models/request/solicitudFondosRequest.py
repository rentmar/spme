from rest_framework import serializers

class CrearSolicitudFondosRequest(serializers.Serializer):
    """
    Request para crear un Solicitud de Fondos.
    """
    detalle_destino_fondos = serializers.JSONField(allow_null=False, required=True)
    forma_pago = serializers.IntegerField(required=True, allow_null=False)
    lugar_solicitud = serializers.CharField(max_length=50)
    fecha_solicitud = serializers.DateField()
    fecha_realizacion_actividad = serializers.DateField(required=False, allow_null=True)  # NUEVO CAMPO
    monto_solicitado = serializers.DecimalField(max_digits=6, decimal_places=2)
    validacion_responsable = serializers.BooleanField(default=False)
    id_responsable = serializers.IntegerField(required=True, allow_null=False)
    validacion_coordinador = serializers.BooleanField(default=False)
    id_coordinador = serializers.IntegerField(required=True, allow_null=False)
    id_usuario = serializers.IntegerField(required=True, allow_null=False)
    id_actividad = serializers.IntegerField(required=True, allow_null=False)

    def validate_detalle_destino_fondos(self, value):
        """
        Valida la estructura del detalle_destino_fondos
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("detalle_destino_fondos debe ser un objeto JSON")
        
        if 'items' in value and isinstance(value['items'], list):
            for item in value['items']:
                if not isinstance(item, dict):
                    raise serializers.ValidationError("Cada item debe ser un objeto")
                # Validar que tenga los campos requeridos
                if 'concepto' not in item:
                    raise serializers.ValidationError("Cada item debe tener un 'concepto'")
                if 'monto' not in item:
                    raise serializers.ValidationError("Cada item debe tener un 'monto'")
                # partida_sf es opcional, no requiere validación estricta
        
        return value

    def to_internal_value(self, data):
        """
        Convierte los campos a un formato interno.
        """
        internal_value = super().to_internal_value(data)
        return {
            'detalleDestinoFondos': internal_value['detalle_destino_fondos'],
            'formaPago_id': int(internal_value['forma_pago']),
            'lugarSolicitud': internal_value['lugar_solicitud'],
            'fechaSolicitud': internal_value['fecha_solicitud'],
            'fechaRealizacionActividad': internal_value.get('fecha_realizacion_actividad'),  # NUEVO CAMPO
            'montoSolicitado': internal_value['monto_solicitado'],
            'validacionResponsable': internal_value['validacion_responsable'],
            'responsable_id': int(internal_value['id_responsable']),
            'validacionCoordinador': internal_value['validacion_coordinador'],
            'coordinador_id': int(internal_value['id_coordinador']),
            'usuario_id': int(internal_value['id_usuario']),
            'actividad_id': int(internal_value['id_actividad']),
        }
          
    