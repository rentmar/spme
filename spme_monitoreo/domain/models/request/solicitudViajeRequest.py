from rest_framework import serializers

class CrearSolicitudViajeRequest(serializers.Serializer):
    """
    Request para crear una Solicitud de Viaje.
    """
    evento = serializers.CharField(max_length=255, required=True)
    fecha_evento = serializers.DateField(required=True)
    lugar_evento = serializers.CharField(max_length=50, required=True)
    instituciones_participantes = serializers.CharField(required=True)
    institucion_queinvita = serializers.CharField(required=True)
    fondos_unitas = serializers.CharField(required=True)
    quien_cubregastos = serializers.CharField(required=True)
    justificacion_asistencia = serializers.CharField(required=True)
    tareas_previas = serializers.CharField(required=True)
    detalle_destino_fondos = serializers.JSONField(required=True)
    validacion_responsable = serializers.BooleanField(default=False)
    validacion_coordinador = serializers.BooleanField(default=False) 
    forma_pago = serializers.IntegerField(required=True)
    lugar_solicitud = serializers.CharField(max_length=50, required=True)
    fecha_solicitud = serializers.DateField(required=True)
    monto_solicitado = serializers.DecimalField(max_digits=12, decimal_places=2, required=True)
    id_responsable = serializers.IntegerField(required=True)
    id_coordinador = serializers.IntegerField(required=True)
    id_usuario = serializers.IntegerField(required=True)
    id_actividad = serializers.IntegerField(required=True)
    id_tarea = serializers.IntegerField(required=False, allow_null=True)
    datos_forma_pago = serializers.JSONField(required=False, allow_null=True, help_text="Datos de forma de pago (transferencia, otros, etc.)")
    #datosSV = serializers.JSONField(required=False, allow_null=True)

    def to_internal_value(self, data):
        """
        Convierte los campos a un formato interno.
        """
        internal_value = super().to_internal_value(data)
        
        # Mapeo correcto según el modelo
        result = {
            'evento': internal_value['evento'],
            'fechaEvento': internal_value['fecha_evento'],
            'lugarEvento': internal_value['lugar_evento'],
            'institucionesParticipantes': internal_value['instituciones_participantes'],
            'organizador': internal_value['institucion_queinvita'],
            'fondosUnitas': internal_value['fondos_unitas'],
            'quienCubreGastos': internal_value['quien_cubregastos'],
            'justificacionAsistencia': internal_value['justificacion_asistencia'],
            'tareasPrevias': internal_value['tareas_previas'],
            'detalleGasto': internal_value['detalle_destino_fondos'],
            'validacionResponsable': internal_value['validacion_responsable'],
            'validacionCoordinador': internal_value['validacion_coordinador'],
            'formaPago_id': int(internal_value['forma_pago']),
            'lugarSolicitud': internal_value['lugar_solicitud'],
            'fechaSolicitud': internal_value['fecha_solicitud'],
            'montoSolicitado': internal_value['monto_solicitado'],
            'validacionResponsable': False,
            'responsable_id': int(internal_value['id_responsable']),
            'validacionCoordinador': False,
            'coordinador_id': int(internal_value['id_coordinador']),
            'usuario_id': int(internal_value['id_usuario']),
            'actividad_id': int(internal_value['id_actividad']),
            'tarea_id': internal_value.get('id_tarea'),
            'datos_forma_pago': internal_value.get('datos_forma_pago', None)
        }
        
        if 'datosSV' in data and data['datosSV'] is not None:
            result['datosSV'] = data['datosSV']
        
        return result
    
class ObtenerSolicitudesViajeRequest(serializers.Serializer):
    """
    Request para obtener solicitudes de viaje con filtros
    """
    id_solicitud_viaje = serializers.IntegerField(required=False, allow_null=True)
    id_actividad = serializers.IntegerField(required=False, allow_null=True)
    id_tarea = serializers.IntegerField(required=False, allow_null=True)
    usuario = serializers.IntegerField(required=False, allow_null=True)

    def to_internal_value(self, data):
        """
        Convierte los campos a un formato interno.
        """
        internal_value = super().to_internal_value(data)
        return {
            "id_solicitud_viaje": internal_value.get("id_solicitud_viaje"),
            "id_actividad": internal_value.get("id_actividad"),
            "id_tarea": internal_value.get("id_tarea"),
            "usuario": internal_value.get("usuario"),
        }