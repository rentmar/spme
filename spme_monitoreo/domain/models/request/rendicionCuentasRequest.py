from rest_framework import serializers

class CrearRendicionCuentasRequest(serializers.Serializer):
    """
    Request para crear un Rendicion de Cuentas.
    """
    cpte_diario = serializers.CharField(max_length=50)
    fecha_desembolso = serializers.DateField()
    monto_asignado = serializers.DecimalField(max_digits=6, decimal_places=2)
    monto_descargado = serializers.DecimalField(max_digits=6, decimal_places=2)
    saldo = serializers.DecimalField(max_digits=6, decimal_places=2)
    detalle_destino_fondos = serializers.JSONField()
    validacion_contador = serializers.BooleanField(default=False)
    id_contador = serializers.IntegerField(required=True, allow_null=False)
    validacion_responsable = serializers.BooleanField(default=False)
    id_responsable = serializers.IntegerField(required=True, allow_null=False)
    validacion_coordinador = serializers.BooleanField(default=False)
    id_coordinador = serializers.IntegerField(required=True, allow_null=False)
    validacion_administrador = serializers.BooleanField(default=False)
    id_administrador = serializers.IntegerField(required=True, allow_null=False)
    id_usuario = serializers.IntegerField(required=True, allow_null=False)
    id_actividad = serializers.IntegerField(required=True, allow_null=False)

    def to_internal_value(self, data):
        """
        Convierte los campos a un formato interno.
        """
        internal_value = super().to_internal_value(data)
        return {
            "cpteDiario": internal_value.get("cpte_diario"),
            "fechaDesembolso": internal_value.get("fecha_desembolso"),
            "montoAsignado": internal_value.get("monto_asignado"),
            "montoDescargado": internal_value.get("monto_descargado"),
            "saldo": internal_value.get("saldo"),
            "detalleDestinoFondos": internal_value.get("detalle_destino_fondos"),
            "validacionContador": internal_value.get("validacion_contador"),
            "idContador": internal_value.get("id_contador"),
            "validacionResponsable": internal_value.get("validacion_responsable"),
            "idResponsable": internal_value.get("id_responsable"),
            "validacionCoordinador": internal_value.get("validacion_coordinador"),
            "idCoordinador": internal_value.get("id_coordinador"),
            "validacionAdministrador": internal_value.get("validacion_administrador"),
            "idAdministrador": internal_value.get("id_administrador"),
            "idUsuario": internal_value.get("id_usuario"),
            "idActividad": internal_value.get("id_actividad"),
        }
          
    