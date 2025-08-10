from rest_framework import serializers

class CrearSolicitudPagoDirectoRequest(serializers.Serializer):
    """
    Request para crear un Solicitud de Pago Directo.
    """
    nombre = serializers.CharField(max_length=50, required=True, allow_null=False)
    paterno = serializers.CharField(max_length=50, required=True, allow_null=False)
    materno = serializers.CharField(max_length=50, required=True, allow_null=False)
    ci = serializers.CharField(max_length=20, required=True, allow_null=False)
    banco = serializers.CharField(max_length=50, required=True, allow_null=False)
    numero_cuenta = serializers.CharField(max_length=50, required=True, allow_null=False)
    cargo = serializers.CharField(max_length=30, required=True, allow_null=False)
    detalle_destino_fondos = serializers.JSONField(allow_null=False, required=True)
    forma_pago = serializers.IntegerField(required=True, allow_null=False)
    lugar_solicitud = serializers.CharField(max_length=50)
    fecha_solicitud = serializers.DateField()
    monto_solicitado = serializers.DecimalField(max_digits=6, decimal_places=2)
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
            'nombre': internal_value['nombre'],
            'paterno': internal_value['paterno'],
            'materno': internal_value['materno'],
            'ci': internal_value['ci'],
            'banco': internal_value['banco'],
            'numeroCuenta': internal_value['numero_cuenta'],
            'cargo': internal_value['cargo'],
            'detalleDestinoFondos': internal_value['detalle_destino_fondos'],
            'formaPago': int(internal_value['forma_pago']),
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
          
    