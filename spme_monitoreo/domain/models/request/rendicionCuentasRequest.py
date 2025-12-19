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
    detalle_destino_fondos = serializers.JSONField(required=False, allow_null=True)
    fecha_actividad = serializers.DateField(required=False, allow_null=True)
    descripcion_actividad = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    lugar_actividad = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    fecha_rendicion = serializers.DateField(required=False, allow_null=True)
    lugar_rendicion = serializers.CharField(required=False, allow_blank=True, allow_null=True)
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
    id_tarea = serializers.IntegerField(required=False, allow_null=True)

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
            "fechaActividad": internal_value.get("fecha_actividad"),
            "descripcionActividad": internal_value.get("descripcion_actividad"),
            "lugarActividad": internal_value.get("lugar_actividad"),
            "fechaRendicion": internal_value.get("fecha_rendicion"),
            "lugarRendicion": internal_value.get("lugar_rendicion"),
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
            "idTarea": internal_value.get("id_tarea"),
        }

class ObtenerRendicionDeCuentasRequest(serializers.Serializer):
    """
    Request para obtener rendiciones de cuentas - soporta ambos modos
    """
    id_rendicionCuentas = serializers.IntegerField(required=False, allow_null=True)
    id_actividad = serializers.IntegerField(required=False, allow_null=True)
    id_tarea = serializers.IntegerField(required=False, allow_null=True)
    usuario = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, data):
        """
        Validación personalizada para asegurar que se envíen parámetros válidos
        """
        # Si no se envía ningún parámetro, permitir obtener todas las rendiciones
        if not any([data.get('id_rendicionCuentas'), data.get('id_actividad'), data.get('id_tarea'), data.get('usuario')]):
            return data  # Permitir obtener todas las rendiciones
        
        return data

    def to_internal_value(self, data):
        """
        Convierte los campos a un formato interno.
        """
        internal_value = super().to_internal_value(data)
        return {
            "id_rendicionCuentas": internal_value.get("id_rendicionCuentas"),
            "id_actividad": internal_value.get("id_actividad"),
            "id_tarea": internal_value.get("id_tarea"),
            "usuario": internal_value.get("usuario"),
        }