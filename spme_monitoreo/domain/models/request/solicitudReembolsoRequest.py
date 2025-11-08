from rest_framework import serializers

class CrearSolicitudReembolsoRequest(serializers.Serializer):
    """
    Request para crear una Solicitud de Reembolso (Reposición).
    """
    #numero_formulario = serializers.CharField(max_length=150, required=False, allow_blank=True, allow_null=True)
    detalle_destino_fondos = serializers.JSONField(allow_null=False, required=True)
    forma_pago = serializers.IntegerField(required=True, allow_null=False)
    lugar_solicitud = serializers.CharField(max_length=50)
    fecha_solicitud = serializers.DateField()
    monto_solicitado = serializers.DecimalField(max_digits=6, decimal_places=2)
    fecha_donde_se_realizo_actividad = serializers.DateField(required=False, allow_null=True)
    descripcion_reposicion = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    objetivo_reposicion = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    # Validaciones
    validacion_responsable = serializers.BooleanField(default=False)
    id_responsable = serializers.IntegerField(required=True, allow_null=False)
    validacion_coordinador = serializers.BooleanField(default=False)
    id_coordinador = serializers.IntegerField(required=True, allow_null=False)
    id_usuario = serializers.IntegerField(required=True, allow_null=False)
    id_actividad = serializers.IntegerField(required=True, allow_null=False)
    id_tarea = serializers.IntegerField(required=False, allow_null=True)

    def to_internal_value(self, data):
        """
        Convierte los campos a un formato interno.
        """
        internal_value = super().to_internal_value(data)
        return {
            #'numeroFormulario': internal_value.get('numero_formulario'),
            'detalleDestinoFondos': internal_value['detalle_destino_fondos'],
            'formaPago_id': int(internal_value['forma_pago']),
            'lugarSolicitud': internal_value['lugar_solicitud'],
            'fechaSolicitud': internal_value['fecha_solicitud'],
            'montoSolicitado': internal_value['monto_solicitado'],
            'fechaDondeSeRealizoActividad': internal_value.get('fecha_donde_se_realizo_actividad'),
            'descripcionReposicion': internal_value.get('descripcion_reposicion'),
            'objetivoReposicion': internal_value.get('objetivo_reposicion'),
            'validacionResponsable': internal_value['validacion_responsable'],
            'responsable_id': int(internal_value['id_responsable']),
            'validacionCoordinador': internal_value['validacion_coordinador'],
            'coordinador_id': int(internal_value['id_coordinador']),
            'usuario_id': int(internal_value['id_usuario']),
            'actividad_id': int(internal_value['id_actividad']),
            'tarea_id': internal_value.get('id_tarea'),
        }

class ObtenerSolicitudReembolsoRequest(serializers.Serializer):
    """
    Request para obtener solicitudes de reembolso - soporta ambos modos
    """
    id = serializers.IntegerField(required=False, allow_null=True)
    id_actividad = serializers.IntegerField(required=False, allow_null=True)
    id_tarea = serializers.IntegerField(required=False, allow_null=True)
    usuario = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, data):
        """
        Validación personalizada para asegurar que se envíen parámetros válidos
        """
        # Si no se envía ningún parámetro, permitir obtener todas las solicitudes
        if not any([data.get('id'), data.get('id_actividad'), data.get('id_tarea'), data.get('usuario')]):
            return data  # Permitir obtener todas las solicitudes
        return data

    def to_internal_value(self, data):
        """
        Convierte los campos a un formato interno.
        """
        internal_value = super().to_internal_value(data)
        return {
            "id": internal_value.get("id"),
            "id_actividad": internal_value.get("id_actividad"),
            "id_tarea": internal_value.get("id_tarea"),
            "usuario": internal_value.get("usuario"),
        }