# serializers.py
#serializers/mensajeria_serializers.py
from rest_framework import serializers
from django.utils import timezone
from datetime import datetime
#from .models import MensajeUsuario, Usuario, TipoMensaje, EstadoMensaje
from spme_mensajes.models import (
    MensajeUsuario,
    Usuario,
    TipoMensaje,
    EstadoMensaje
)

class MensajeCreateSerializer(serializers.ModelSerializer):
    destinatario_id = serializers.IntegerField(required=True, write_only=True)
    
    # Campos para respuestas (remitente_id ya no se recibe del frontend)
    remitente_info = serializers.SerializerMethodField(read_only=True)
    destinatario_info = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = MensajeUsuario
        fields = [
            'id',
            'destinatario_id',
            'tipo',
            'asunto',
            'contenido',
            'actividad_id',
            'proyecto_id',
            'prioridad',
            'routing_key',
            'metadata',
            'referencia_id',
            'fecha_expiracion',
            'icono',
            'accion_url',
            'accion_texto',
            'remitente_info',
            'destinatario_info',
            'message_id',
            'fecha_envio',
            'estado'
        ]
        read_only_fields = [
            'id', 'message_id', 'fecha_envio', 'estado', 
            'fecha_leido', 'fecha_actualizacion'
        ]
        extra_kwargs = {
            'remitente': {'required': False, 'write_only': True}
        }
    
    def get_remitente_info(self, obj):
        if obj.remitente:
            return {
                'id': obj.remitente.id,
                'username': obj.remitente.username,
                'nombre_completo': obj.remitente.get_full_name() if hasattr(obj.remitente, 'get_full_name') else obj.remitente.username,
            }
        return None
    
    def get_destinatario_info(self, obj):
        return {
            'id': obj.destinatario.id,
            'username': obj.destinatario.username,
            'nombre_completo': obj.destinatario.get_full_name() if hasattr(obj.destinatario, 'get_full_name') else obj.destinatario.username,
        }
    
    def validate_destinatario_id(self, value):
        try:
            Usuario.objects.get(pk=value)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError(f"Usuario con ID {value} no existe.")
        return value
    
    def validate(self, data):
        request = self.context.get('request')
        
        # Validar destinatario
        destinatario_id = data.get('destinatario_id')
        try:
            destinatario = Usuario.objects.get(pk=destinatario_id)
            data['destinatario'] = destinatario
        except Usuario.DoesNotExist:
            raise serializers.ValidationError({"destinatario_id": f"Usuario con ID {destinatario_id} no existe."})
        
        # Remitente se extrae del JWT (usuario autenticado)
        if request and request.user.is_authenticated:
            data['remitente'] = request.user
            
            # Validar que el usuario no se envíe mensajes a sí mismo (excepto para sistema)
            if request.user.id == destinatario.id and data.get('tipo') != TipoMensaje.SISTEMA:
                raise serializers.ValidationError({
                    "destinatario_id": "No puedes enviarte mensajes a ti mismo."
                })
        
        # Validar prioridad
        prioridad = data.get('prioridad', 1)
        if prioridad < 1 or prioridad > 3:
            raise serializers.ValidationError({"prioridad": "La prioridad debe ser entre 1 y 3."})
        
        # Validar fecha de expiración
        fecha_expiracion = data.get('fecha_expiracion')
        if fecha_expiracion:
            if isinstance(fecha_expiracion, str):
                try:
                    fecha_expiracion = datetime.fromisoformat(fecha_expiracion.replace('Z', '+00:00'))
                except ValueError:
                    raise serializers.ValidationError({"fecha_expiracion": "Formato de fecha inválido. Use ISO 8601."})
            
            if fecha_expiracion <= timezone.now():
                raise serializers.ValidationError({"fecha_expiracion": "La fecha de expiración debe ser futura."})
        
        # Validar tipo de mensaje
        tipo = data.get('tipo', TipoMensaje.PRIVADO)
        if tipo not in dict(TipoMensaje.choices):
            raise serializers.ValidationError({
                "tipo": f"Tipo de mensaje inválido. Opciones: {list(dict(TipoMensaje.choices).keys())}"
            })
        
        return data
    
    def create(self, validated_data):
        # Remover el campo de ID ya que ya convertimos a objeto
        validated_data.pop('destinatario_id', None)
        
        # Si es mensaje del sistema, remitente = None
        if validated_data.get('tipo') == TipoMensaje.SISTEMA:
            validated_data['remitente'] = None
            if not validated_data.get('icono'):
                validated_data['icono'] = '🔔'
        
        # Crear el mensaje
        return MensajeUsuario.objects.create(**validated_data)