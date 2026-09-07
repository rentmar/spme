from rest_framework import serializers

class CrearSolicitudPagoDirectoRequest(serializers.Serializer):
    """
    Request para crear una Solicitud de Pago Directo.
    """
    descripcion_actividad = serializers.CharField(required=True, allow_blank=False)
    fecha_realizacion_actividad = serializers.DateField(required=True) # Renombrado de fecha_realizacion
    objetivo_actividad = serializers.CharField(required=True, allow_blank=False)
    
    detalle_destino_fondos = serializers.JSONField(required=True)
    forma_pago = serializers.IntegerField(required=True)
    lugar_solicitud = serializers.CharField(required=True)
    fecha_solicitud = serializers.DateField(required=True)
    monto_solicitado = serializers.DecimalField(max_digits=12, decimal_places=2, required=True)
    
    # Validaciones
    validacion_responsable = serializers.BooleanField(default=False)
    contador_id = serializers.IntegerField(required=True) # Renombrado de id_contador
    validacion_coordinador = serializers.BooleanField(default=False)
    id_coordinador = serializers.IntegerField(required=True)
    id_usuario = serializers.IntegerField(required=True)
    id_actividad = serializers.IntegerField(required=True)
    id_tarea = serializers.IntegerField(required=False, allow_null=True)
    
    # Nuevo campo de payload
    bloquear_icono_sf = serializers.BooleanField(default=True)
    
    # Nuevo campo
    datos_forma_pago = serializers.JSONField(required=True)

    def to_internal_value(self, data):
        """
        Convierte los campos a un formato interno.
        """
        internal_value = super().to_internal_value(data)
        
        return {
            'descripcion_actividad': internal_value['descripcion_actividad'],
            'fechaRealizacionActividad': internal_value['fecha_realizacion_actividad'], # Mapping correcto
            'objetivo_actividad': internal_value['objetivo_actividad'],
            
            'detalleDestinoFondos': internal_value['detalle_destino_fondos'],
            'formaPago_id': int(internal_value['forma_pago']),
            'lugarSolicitud': internal_value['lugar_solicitud'],
            'fechaSolicitud': internal_value['fecha_solicitud'],
            'montoSolicitado': internal_value['monto_solicitado'],
            'validacionResponsable': internal_value['validacion_responsable'],
            'contador_id': int(internal_value['contador_id']), # Mapping correcto
            'validacionCoordinador': internal_value['validacion_coordinador'],
            'coordinador_id': int(internal_value['id_coordinador']),
            'usuario_id': int(internal_value['id_usuario']),
            'actividad_id': int(internal_value['id_actividad']),
            'tarea_id': internal_value.get('id_tarea'),
            'datos_forma_pago': internal_value['datos_forma_pago'],
            'bloquearIconosSolFondos': internal_value.get('bloquear_icono_sf', True)  # Mapeado de payload a modelo
        }
    
class ObtenerSolicitudesPagoDirectoRequest(serializers.Serializer):
    """
    Request para obtener solicitudes de pago directo - soporta ambos modos
    """
    id_solicitudPagoDirecto = serializers.IntegerField(required=False, allow_null=True)
    id_actividad = serializers.IntegerField(required=False, allow_null=True)
    id_tarea = serializers.IntegerField(required=False, allow_null=True)
    usuario = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, data):
        """
        Validación personalizada para asegurar que se envíen parámetros válidos
        """
        # Si no se envía ningún parámetro, permitir obtener todas las solicitudes
        if not any([data.get('id_solicitudPagoDirecto'), data.get('id_actividad'), data.get('id_tarea'), data.get('usuario')]):
            return data  # Permitir obtener todas las solicitudes
        
        return data

    def to_internal_value(self, data):
        """
        Convierte los campos a un formato interno.
        """
        internal_value = super().to_internal_value(data)
        return {
            "id_solicitudPagoDirecto": internal_value.get("id_solicitudPagoDirecto"),
            "id_actividad": internal_value.get("id_actividad"),
            "id_tarea": internal_value.get("id_tarea"),
            "usuario": internal_value.get("usuario"),
        }