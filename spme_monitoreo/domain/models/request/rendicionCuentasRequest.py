from rest_framework import serializers

class CrearRendicionCuentasRequest(serializers.Serializer):
    """
    Request para crear un Rendicion de Cuentas.
    """
    nombre = serializers.CharField(max_length=50)
    paterno = serializers.CharField(max_length=50)
    materno = serializers.CharField(max_length=50)
    documento_identidad = serializers.CharField(max_length=20)
    cargo = serializers.CharField(max_length=50)
    numero_formulario = serializers.CharField(max_length=20)
    cpte_diario = serializers.CharField(max_length=50)
    fecha_desembolso = serializers.DateField()
    monto_asignado = serializers.DecimalField(max_digits=10, decimal_places=2)
    monto_descargado = serializers.DecimalField(max_digits=10, decimal_places=2)
    saldo_restante = serializers.DecimalField(max_digits=10, decimal_places=2)
    fuente_financiamiento = serializers.CharField(max_length=50)
    descripcion = serializers.CharField(max_length=350)
    fecha_realizacion = serializers.DateField()
    lugar_actividad = serializers.CharField(max_length=50)
    detalle_destino_fondos = serializers.JSONField()
    contador_aprobacion = serializers.BooleanField(default=False)
    contador = serializers.IntegerField(required=True, allow_null=False)
    responsable_aprobacion = serializers.BooleanField(default=False)
    responsable = serializers.IntegerField(required=True, allow_null=False)
    coordinador_aprobacion = serializers.BooleanField(default=False)
    coordinador = serializers.IntegerField(required=True, allow_null=False)
    administrador_aprobacion = serializers.BooleanField(default=False)
    administrador = serializers.IntegerField(required=True, allow_null=False)

    def to_internal_value(self, data):
        """
        Convierte los campos a un formato interno.
        """
        internal_value = super().to_internal_value(data)
        return {
            "nombre": internal_value.get("nombre"),
            "paterno": internal_value.get("paterno"),
            "materno": internal_value.get("materno"),
            "documentoIdentidad": internal_value.get("documento_identidad"),
            "cargo": internal_value.get("cargo"),
            "numeroFormulario": internal_value.get("numero_formulario"),
            "cpteDiario": internal_value.get("cpte_diario"),
            "fechaDesembolso": internal_value.get("fecha_desembolso"),
            "montoAsignado": internal_value.get("monto_asignado"),
            "montoDescargado": internal_value.get("monto_descargado"),
            "saldoRestante": internal_value.get("saldo_restante"),
            "fuenteFinanciamiento": internal_value.get("fuente_financiamiento"),
            "descripcion": internal_value.get("descripcion"),
            "fechaRealizacion": internal_value.get("fecha_realizacion"),
            "lugarActividad": internal_value.get("lugar_actividad"),
            "detalleDestinoFondos": internal_value.get("detalle_destino_fondos"),
            "contadorAprobacion": internal_value.get("contador_aprobacion"),
            "contador": internal_value.get("contador"),
            "responsableAprobacion": internal_value.get("responsable_aprobacion"),
            "responsable": internal_value.get("responsable"),
            "coordinadorAprobacion": internal_value.get("coordinador_aprobacion"),
            "coordinador": internal_value.get("coordinador"),
            "administradorAprobacion": internal_value.get("administrador_aprobacion"),
            "administrador": internal_value.get("administrador")
        }
          
    