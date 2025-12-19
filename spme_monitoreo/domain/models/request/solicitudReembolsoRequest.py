from rest_framework import serializers

class CrearSolicitudReembolsoRequest(serializers.Serializer):
    """
    Request para crear una Solicitud de Reembolso.
    """
    detalle_destino_fondos = serializers.JSONField(required=False)
    forma_pago = serializers.IntegerField(required=False)
    lugar_solicitud = serializers.CharField(max_length=50, required=False)
    fecha_solicitud = serializers.DateField(required=False)
    fecha_realizacion_actividad = serializers.DateField(required=False)
    monto_solicitado = serializers.DecimalField(max_digits=6, decimal_places=2, required=False)
    validacion_responsable = serializers.BooleanField(default=False, required=False)
    contador_id = serializers.IntegerField(required=False)
    validacion_coordinador = serializers.BooleanField(default=False, required=False)
    id_coordinador = serializers.IntegerField(required=False)
    id_usuario = serializers.IntegerField(required=False)
    id_actividad = serializers.IntegerField(required=False)
    descripcion_actividad = serializers.CharField(max_length=255, required=False)
    objetivo_actividad = serializers.CharField(max_length=255, required=False)
    datos_forma_pago = serializers.JSONField(required=False)
    bloquear_icono_sf = serializers.BooleanField(default=True, required=False)
    codigo_actividad = serializers.CharField(max_length=50, required=False)
    
    def to_internal_value(self, data):
        """
        Convierte los campos a un formato interno que coincide con el modelo.
        """
        internal_value = super().to_internal_value(data)
        return {
            "detalleDestinoFondos": internal_value.get("detalle_destino_fondos"),
            "formaPago_id": internal_value.get("forma_pago"),
            "lugarSolicitud": internal_value.get("lugar_solicitud"),
            "fechaSolicitud": internal_value.get("fecha_solicitud"),
            "fechaRealizacionActividad": internal_value.get("fecha_realizacion_actividad"),
            "montoSolicitado": internal_value.get("monto_solicitado"),
            "validacionResponsable": internal_value.get("validacion_responsable"),
            "contador_id": internal_value.get("contador_id"),
            "validacionCoordinador": internal_value.get("validacion_coordinador"),
            "coordinador_id": internal_value.get("id_coordinador"),
            "usuario_id": internal_value.get("id_usuario"),
            "actividad_id": internal_value.get("id_actividad"),
            "descripcion_actividad": internal_value.get("descripcion_actividad"),
            "objetivo_actividad": internal_value.get("objetivo_actividad"),
            "datos_forma_pago": internal_value.get("datos_forma_pago"),
            "bloquearIconos": internal_value.get("bloquear_icono_sf"),
            "codigo_actividad": internal_value.get("codigo_actividad")
        }

        # CAMPOS OPCIONALES
        if internal_value.get('fecha_realizacion_actividad') is not None:
            result['fechaRealizacionActividad'] = internal_value.get('fecha_realizacion_actividad')
        
        if internal_value.get('descripcion_actividad') is not None:
            result['descripcion_actividad'] = internal_value.get('descripcion_actividad')
        
        if internal_value.get('objetivo_actividad') is not None:
            result['objetivo_actividad'] = internal_value.get('objetivo_actividad')
        
        if internal_value.get('datos_forma_pago') is not None:
            result['datos_forma_pago'] = internal_value.get('datos_forma_pago')
        
        if internal_value.get('id_tarea') is not None:
            result['tarea_id'] = internal_value.get('id_tarea')
        
        print("Datos mapeados para crear solicitud reembolso:", result)
        return result


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
        if not any([data.get('id'), data.get('id_actividad'), data.get('id_tarea'), data.get('usuario')]):
            return data
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