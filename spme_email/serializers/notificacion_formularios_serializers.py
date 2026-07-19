# spme/spme_email/serializers/notificacion_formularios_serializers.py
from rest_framework import serializers

class NotificacionBaseSerializer(serializers.Serializer):
    """
    Valida los datos de entrada del endpoint de notificaciones.
    {
        "tipo_solicitud": "fondos",
        "solicitud_id": 42,
        "accion": "revision",
        "destinatarios_ids": [68, 71],
        "base_url": "https://spme.gob.bo"
    }
    """
    #Id de la solicitud
    solicitud_id = serializers.IntegerField(required=True, min_value=1)
    #Tipo de la solicitud
    tipo_solicitud = serializers.ChoiceField(
        choices=['fondos', 'reposicion', 'viaje', 'pago_directo', 'rendicion'],
        required = True,
    )
    #Tipo de notificacion
    accion = serializers.ChoiceField(
        choices=['revision', 'aprobacion', 'rechazo', 'nueva_revision'],
        required=True
    )
    #Destinatarios
    destinatarios_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required = True,
    )
    motivo_rechazo = serializers.CharField(
        required=False, allow_blank=True, default=''
    )
    #La url base del front end
    base_url = serializers.CharField(
        required=True, 
    )
    #Modo de envio de notificacion
    #celery asyn_mode = Tue
