# serializers.py
from rest_framework import serializers
from ..models import MensajeUsuario
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class MensajeUsuarioSerializer(serializers.ModelSerializer):
    remitente_info = serializers.SerializerMethodField()
    destinatario_info = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display')
    tipo_display = serializers.CharField(source='get_tipo_display')
    
    class Meta:
        model = MensajeUsuario
        fields = [
            'id', 'message_id', 'tipo', 'tipo_display', 'estado', 'estado_display',
            'remitente', 'remitente_info', 'destinatario', 'destinatario_info',
            'asunto', 'contenido', 'fecha_envio', 'fecha_leido', 'fecha_expiracion',
            'fecha_actualizacion', 'actividad_id', 'proyecto_id', 'prioridad',
            'routing_key', 'metadata', 'referencia_id', 'icono', 
            'accion_url', 'accion_texto'
        ]
    
    def get_remitente_info(self, obj):
        if obj.remitente:
            return {
                'id': obj.remitente.pk,
                'username': obj.remitente.username,
                'nombre_completo': obj.remitente.get_full_name(),
            }
        return {
            'id': None,
            'username': 'Sistema',
            'nombre_completo': 'Sistema',
        }
    
    def get_destinatario_info(self, obj):
        return {
            'id': obj.destinatario.pk,
            'username': obj.destinatario.username,
            'nombre_completo': obj.destinatario.get_full_name(),
        }