from rest_framework import serializers

class CrearSolicitudViajeRequest(serializers.Serializer):
    """
    Request para crear una Solicitud de Viaje.
    """
    evento = serializers.CharField(max_length=150)
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField()
    lugar_evento = serializers.CharField(max_length=150)
    instituciones_participantes = serializers.CharField(max_length=255)
    organizador = serializers.CharField(max_length=100)
    quien_cubre_gastos = serializers.CharField(max_length=100)
    justificacion_asistencia = serializers.CharField(max_length=255)
    fondos_Unitas = serializers.CharField(max_length=100)
    tareas_previas = serializers.CharField(max_length=255)
    forma_pago = serializers.IntegerField()
    monto_solicitado = serializers.DecimalField(max_digits=6, decimal_places=2)
    lugar_solicitud = serializers.CharField(max_length=150)
    fecha_solicitud = serializers.DateField()
    validacion_responsable = serializers.BooleanField(default=False)
    id_responsable = serializers.IntegerField()
    validacion_coordinador = serializers.BooleanField(default=False)
    id_coordinador = serializers.IntegerField()
    id_usuario = serializers.IntegerField(required=True, allow_null=False)

    def to_internal_value(self, data):
        """
        Convierte los campos a un formato interno.
        """
        internal_value = super().to_internal_value(data)
        return {
            "evento": internal_value.get("evento"),
            "fechaInicio": internal_value.get("fecha_inicio"),
            "fechaFin": internal_value.get("fecha_fin"),
            "lugarEvento": internal_value.get("lugar_evento"),
            "institucionesParticipantes": internal_value.get("instituciones_participantes"),
            "organizador": internal_value.get("organizador"),
            "quienCubreGastos": internal_value.get("quien_cubre_gastos"),
            "justificacionAsistencia": internal_value.get("justificacion_asistencia"),
            "fondosUnitas": internal_value.get("fondos_Unitas"),
            "tareasPrevias": internal_value.get("tareas_previas"),
            "formaPago": internal_value.get("forma_pago"),
            "montoSolicitado": internal_value.get("monto_solicitado"),
            "lugarSolicitud": internal_value.get("lugar_solicitud"),
            "fechaSolicitud": internal_value.get("fecha_solicitud"),
            "validacionResponsable": internal_value.get("validacion_responsable"),
            "idResponsable": internal_value.get("id_responsable"),
            "validacionCoordinador": internal_value.get("validacion_coordinador"),
            "idCoordinador": internal_value.get("id_coordinador"),
            "idUsuario": internal_value.get("id_usuario"),
        }