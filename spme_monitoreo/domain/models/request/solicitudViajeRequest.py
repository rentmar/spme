from rest_framework import serializers

class CrearSolicitudViajeRequest(serializers.Serializer):
    """
    Request para crear una Solicitud de Viaje.
    """
    numero_formulario = serializers.CharField(max_length=50)
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
    monto_solicitado = serializers.DecimalField(max_digits=6, decimal_places=2)
    lugar_solicitud = serializers.CharField(max_length=150)
    fecha_solicitud = serializers.DateField()
    validacion_responsable = serializers.BooleanField(default=False)
    validacion_coordinador = serializers.BooleanField(default=False)
    actividad_id = serializers.IntegerField()
    coordinador_id = serializers.IntegerField()
    forma_pago_id = serializers.IntegerField()
    responsable_id = serializers.IntegerField()
    tarea_id = serializers.IntegerField()
    usuario_id = serializers.IntegerField(required=True, allow_null=False)
    bloquear_iconos = serializers.BooleanField(default=False)

    def to_internal_value(self, data):
        """
        Convierte los campos a un formato interno.
        """
        internal_value = super().to_internal_value(data)
        return {
            "numeroFormulario": internal_value.get("numero_formulario"),
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
            "montoSolicitado": internal_value.get("monto_solicitado"),
            "lugarSolicitud": internal_value.get("lugar_solicitud"),
            "fechaSolicitud": internal_value.get("fecha_solicitud"),
            "validacionResponsable": internal_value.get("validacion_responsable"),
            "validacionCoordinador": internal_value.get("validacion_coordinador"),
            "actividad_id": internal_value.get("actividad_id"),
            "coordinador_id": internal_value.get("coordinador_id"),
            "formaPago_id": internal_value.get("forma_pago_id"),
            "responsable_id": internal_value.get("responsable_id"),
            "tarea_id": internal_value.get("tarea_id"),
            "usuario_id": internal_value.get("usuario_id"),
            "bloquearIconos": internal_value.get("bloquear_iconos"),
        }