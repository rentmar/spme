#serializers.py
# serializers/mensaje_automatico_sistema_serializer.py
from rest_framework import serializers
from spme_autenticacion.models import Usuario
from spme_mensajes.models import MensajeUsuario
#from .models import MensajeUsuario, Usuario


class MensajeUsuarioSerializer(serializers.ModelSerializer):
    remitente_info = serializers.SerializerMethodField()
    destinatario_info = serializers.SerializerMethodField()
    
    class Meta:
        model = MensajeUsuario
        fields = [
            'id', 'tipo', 'asunto', 'contenido', 'fecha_envio', 
            'fecha_leido', 'estado', 'actividad_id', 'proyecto_id',
            'prioridad', 'message_id', 'routing_key', 'metadata',
            'referencia_id', 'fecha_expiracion', 'icono', 'accion_url',
            'accion_texto', 'remitente_info', 'destinatario_info'
        ]
        read_only_fields = [
            'id', 'fecha_envio', 'fecha_leido', 'message_id', 
            'fecha_actualizacion'
        ]
    
    def get_remitente_info(self, obj):
        if obj.remitente:
            # Construir nombre_completo dinámicamente SIN propiedad en el modelo
            nombre_completo = self._construir_nombre_completo(obj.remitente)
            
            return {
                'id': obj.remitente.id,
                'username': obj.remitente.username,
                'nombre': obj.remitente.nombre or '',
                'paterno': obj.remitente.paterno or '',
                'materno': obj.remitente.materno or '',
                'nombre_completo': nombre_completo,
                'ci': obj.remitente.ci or '',
                'cargo': obj.remitente.cargo or ''
            }
        return None
    
    def get_destinatario_info(self, obj):
        # Construir nombre_completo dinámicamente SIN propiedad en el modelo
        nombre_completo = self._construir_nombre_completo(obj.destinatario)
        
        return {
            'id': obj.destinatario.id,
            'username': obj.destinatario.username,
            'nombre': obj.destinatario.nombre or '',
            'paterno': obj.destinatario.paterno or '',
            'materno': obj.destinatario.materno or '',
            'nombre_completo': nombre_completo,
            'ci': obj.destinatario.ci or '',
            'cargo': obj.destinatario.cargo or ''
        }
    
    def _construir_nombre_completo(self, usuario):
        """Helper para construir nombre completo desde campos separados"""
        partes = []
        
        # Usar los campos que tienes en tu modelo
        if usuario.nombre:
            partes.append(usuario.nombre)
        if usuario.paterno:
            partes.append(usuario.paterno)
        if usuario.materno:
            partes.append(usuario.materno)
        
        # Si hay partes, unirlas; si no, usar username
        if partes:
            return " ".join(partes).strip()
        return usuario.username