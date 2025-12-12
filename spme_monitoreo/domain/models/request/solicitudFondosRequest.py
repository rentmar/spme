from rest_framework import serializers

class CrearSolicitudFondosRequest(serializers.Serializer):
    """
    Request para crear un Solicitud de Fondos.
    """
    numero_formulario = serializers.CharField(max_length=150, required=False, allow_blank=True, allow_null=True)
    detalle_destino_fondos = serializers.JSONField(allow_null=False, required=True)
    forma_pago = serializers.IntegerField(required=True, allow_null=False)
    lugar_solicitud = serializers.CharField(max_length=50)
    fecha_solicitud = serializers.DateField()
    fecha_realizacion_actividad = serializers.DateField(required=False, allow_null=True)  # NUEVO CAMPO
    monto_solicitado = serializers.DecimalField(max_digits=6, decimal_places=2)
    validacion_responsable = serializers.BooleanField(default=False)
    contador_id = serializers.IntegerField(required=True, allow_null=False)
    validacion_coordinador = serializers.BooleanField(default=False)
    id_coordinador = serializers.IntegerField(required=True, allow_null=False)
    id_usuario = serializers.IntegerField(required=True, allow_null=False)
    id_actividad = serializers.IntegerField(required=True, allow_null=False)

    descripcion_actividad = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    objetivo_actividad = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    id_tarea = serializers.IntegerField(required=False, allow_null=True)
    datos_forma_pago = serializers.JSONField(required=False, allow_null=True)
    bloquear_iconos_sol_fondos = serializers.BooleanField(default=True)

    def validate_detalle_destino_fondos(self, value):
        """
        Valida la estructura del detalle_destino_fondos
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("detalle_destino_fondos debe ser un objeto JSON")
        
        if 'items' in value and isinstance(value['items'], list):
            for item in value['items']:
                if not isinstance(item, dict):
                    raise serializers.ValidationError("Cada item debe ser un objeto")
                # Validar que tenga los campos requeridos
                if 'concepto' not in item:
                    raise serializers.ValidationError("Cada item debe tener un 'concepto'")
                if 'monto' not in item:
                    raise serializers.ValidationError("Cada item debe tener un 'monto'")
                # partida_sf es opcional, no requiere validación estricta
        
        return value

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
            'fechaRealizacionActividad': internal_value.get('fecha_realizacion_actividad'),
            'montoSolicitado': internal_value['monto_solicitado'],
            'validacionResponsable': internal_value['validacion_responsable'],
            'contador_id': int(internal_value['contador_id']),
            'validacionCoordinador': internal_value['validacion_coordinador'],
            'coordinador_id': int(internal_value['id_coordinador']),
            'usuario_id': int(internal_value['id_usuario']),
            'actividad_id': int(internal_value['id_actividad']),
        }

        # CAMPOS OPCIONALES - CORREGIDOS
        # numero_formulario
        if internal_value.get('numero_formulario') is not None:
            result['numeroFormulario'] = internal_value.get('numero_formulario')
        
        # descripcion_actividad
        if internal_value.get('descripcion_actividad') is not None:
            result['descripcion_actividad'] = internal_value.get('descripcion_actividad')
        elif data.get('descripcionActividad') is not None:
            result['descripcion_actividad'] = data.get('descripcionActividad')
        elif internal_value.get('descripcion_actividad') == '':
            result['descripcion_actividad'] = None
        
        # objetivo_actividad
        if internal_value.get('objetivo_actividad') is not None:
            result['objetivo_actividad'] = internal_value.get('objetivo_actividad')
        elif data.get('objetivoActividad') is not None:
            result['objetivo_actividad'] = data.get('objetivoActividad')
        elif internal_value.get('objetivo_actividad') == '':
            result['objetivo_actividad'] = None
        
        # datos_forma_pago
        if internal_value.get('datos_forma_pago') is not None:
            result['datos_forma_pago'] = internal_value.get('datos_forma_pago')
        elif data.get('datosFormaPago') is not None:
            result['datos_forma_pago'] = data.get('datosFormaPago')
        elif internal_value.get('datos_forma_pago') == '':
            result['datos_forma_pago'] = None
        
        # tarea_id
        if internal_value.get('id_tarea') is not None:
            result['tarea_id'] = internal_value.get('id_tarea')
        
        # bloquear_iconos_sol_fondos
        if internal_value.get('bloquear_iconos_sol_fondos') is not None:
            result['bloquearIconosSolFondos'] = internal_value.get('bloquear_iconos_sol_fondos')
        
        print("Datos mapeados para crear:", result)  # DEBUG
        return result