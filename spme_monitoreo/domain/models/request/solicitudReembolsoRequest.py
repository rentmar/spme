from rest_framework import serializers

class CrearSolicitudReembolsoRequest(serializers.Serializer):
    """
    Request para crear un Solicitud de Reembolso.
    """
    detalle_destino_fondos = serializers.JSONField()
    forma_pago = serializers.IntegerField(required=True, allow_null=False)
    lugar_solicitud = serializers.CharField(max_length=50)
    fecha_solicitud = serializers.DateField()
    monto_solicitado = serializers.DecimalField(max_digits=10, decimal_places=2)
    validacion_responsable = serializers.BooleanField(default=False)
    id_responsable = serializers.IntegerField(required=True, allow_null=False)
    validacion_coordinador = serializers.BooleanField(default=False)
    id_coordinador = serializers.IntegerField(required=True, allow_null=False)
    id_usuario = serializers.IntegerField(required=True, allow_null=False)
    id_actividad = serializers.IntegerField(required=True, allow_null=False)

    def to_internal_value(self, data):
        """
        Convierte los campos a un formato interno.
        """
        internal_value = super().to_internal_value(data)
        return {
            'formaPago': internal_value['forma_pago'],
            'detalleDestinoFondos': internal_value['detalle_destino_fondos'],
            'lugarSolicitud': internal_value['lugar_solicitud'],
            'fechaSolicitud': internal_value['fecha_solicitud'],
            'montoSolicitado': internal_value['monto_solicitado'],
            'validacionResponsable': internal_value['validacion_responsable'],
            'idResponsable': int(internal_value['id_responsable']),
            'validacionCoordinador': internal_value['validacion_coordinador'],
            'idCoordinador': int(internal_value['id_coordinador']),
            'idUsuario': int(internal_value['id_usuario']),
            'idActividad': int(internal_value['id_actividad']),
        }
          
    