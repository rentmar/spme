from rest_framework import serializers

class CrearSolicitudReembolsoRequest(serializers.Serializer):
    """
    Request para crear una Solicitud de Reembolso (Reposición).
    """
    detalle_destino_fondos = serializers.JSONField(allow_null=False, required=True)
    forma_pago = serializers.IntegerField(required=True, allow_null=False)
    lugar_solicitud = serializers.CharField(max_length=50)
    fecha_solicitud = serializers.DateField()
    fecha_realizacion_actividad = serializers.DateField(required=False, allow_null=True)
    monto_solicitado = serializers.DecimalField(max_digits=6, decimal_places=2)
    descripcion_actividad = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    objetivo_actividad = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    datos_forma_pago = serializers.JSONField(required=False, allow_null=True)
    bloquear_icono_sf = serializers.BooleanField(default=True, required=False)
    codigo_actividad = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    # Validaciones
    validacion_responsable = serializers.BooleanField(default=False)
    contador_id = serializers.IntegerField(required=True, allow_null=False)
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
        result = {
            'detalleDestinoFondos': internal_value['detalle_destino_fondos'],
            'formaPago_id': int(internal_value['forma_pago']),
            'lugarSolicitud': internal_value['lugar_solicitud'],
            'fechaSolicitud': internal_value['fecha_solicitud'],
            'montoSolicitado': internal_value['monto_solicitado'],
            'validacionContador': internal_value['validacion_responsable'],
            'contador_id': int(internal_value['contador_id']),
            'validacionCoordinador': internal_value['validacion_coordinador'],
            'coordinador_id': int(internal_value['id_coordinador']),
            'usuario_id': int(internal_value['id_usuario']),
            'actividad_id': int(internal_value['id_actividad']),
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
        
        if internal_value.get('bloquear_icono_sf') is not None:
            result['bloquearIconosSolFondos'] = internal_value.get('bloquear_icono_sf')
        
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