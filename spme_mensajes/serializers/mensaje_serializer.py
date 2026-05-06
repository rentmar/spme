#serializers/mensaje_serializer.py
"""
Serializers para el sistema de mensajería interna
"""
from rest_framework import serializers
from ..models import MensajeUsuario, TipoMensaje, EstadoMensaje
from spme_autenticacion.models import Usuario
import json


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer básico para mostrar información del usuario
    Usado en relaciones con otros modelos
    """
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = [
            'id',
            'username',
            'nombre',
            'paterno',
            'materno',
            'nombre_completo',
            'ci',
            'cargo',
            'banco',
            'numero_cuenta',
            'tipo_cuenta',
            'permisos',
        ]
        read_only_fields = fields

    def get_nombre_completo(self, obj):
        """Obtiene el nombre completo del usuario"""
        return obj.get_full_name()    



class MensajeSerializer(serializers.ModelSerializer):
    """
    Serializer para mensajes de usuario
    """
    remitente_detalle = UsuarioSerializer(source='remitente', read_only=True)
    destinatario_detalle = UsuarioSerializer(source='destinatario', read_only=True)
    
    # Campos calculados
    es_leido = serializers.BooleanField(read_only=True)
    es_urgente = serializers.BooleanField(read_only=True)
    es_expirado = serializers.SerializerMethodField()
    tiene_accion = serializers.SerializerMethodField()
    tiempo_transcurrido = serializers.SerializerMethodField()
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = MensajeUsuario
        fields = [
            'id',
            'message_id',
            'tipo',
            'tipo_display',
            'asunto',
            'contenido',
            'estado',
            'estado_display',
            'prioridad',
            'fecha_envio',
            'fecha_leido',
            'fecha_expiracion',
            'actividad_id',
            'proyecto_id',
            'remitente',
            'remitente_detalle',
            'destinatario',
            'destinatario_detalle',
            'routing_key',
            'metadata',
            'referencia_id',
            'accion_url',
            'accion_texto',
            'icono',
            'es_leido',
            'es_urgente',
            'es_expirado',
            'tiene_accion',
            'tiempo_transcurrido',
        ]
        read_only_fields = [
            'id', 'message_id', 'fecha_envio', 'fecha_leido',
            'fecha_actualizacion', 'es_leido', 'es_urgente',
            'tipo_display', 'estado_display',
            'remitente_detalle', 'destinatario_detalle'
        ]
    
    def get_es_expirado(self, obj):
        return obj.es_expirado
    
    def get_tiene_accion(self, obj):
        return obj.tiene_accion
    
    def get_tiempo_transcurrido(self, obj):
        from django.utils import timezone
        from django.utils.timesince import timesince
        
        if obj.fecha_envio:
            return timesince(obj.fecha_envio, timezone.now())
        return ""
    
    def to_representation(self, instance):
        """Personaliza la representación del mensaje"""
        representation = super().to_representation(instance)
        
        # Parsear metadata si es string
        if isinstance(representation['metadata'], str):
            try:
                representation['metadata'] = json.loads(representation['metadata'])
            except:
                representation['metadata'] = {}
        
        # Formatear fechas
        if representation['fecha_envio']:
            representation['fecha_envio'] = instance.fecha_envio.isoformat()
        
        if representation['fecha_leido']:
            representation['fecha_leido'] = instance.fecha_leido.isoformat()
        
        if representation['fecha_expiracion']:
            representation['fecha_expiracion'] = instance.fecha_expiracion.isoformat()
        
        return representation

class CrearMensajeSerializer(serializers.ModelSerializer):
    """
    Serializer para crear nuevos mensajes
    """
    class Meta:
        model = MensajeUsuario
        fields = [
            'destinatario',
            'remitente',
            'asunto',
            'contenido',
            'tipo',
            'prioridad',
            'actividad_id',
            'proyecto_id',
            'routing_key',
            'metadata',
            'referencia_id',
            'fecha_expiracion',
            'accion_url',
            'accion_texto',
            'icono',
        ]
        extra_kwargs = {
            'remitente': {'required': False, 'allow_null': True},
            'routing_key': {'required': True},
            'metadata': {'required': False, 'default': {}},
            'tipo': {'default': TipoMensaje.PRIVADO},
            'prioridad': {'default': 1},
        }
    
    def validate(self, data):
        """Validación personalizada"""
        from spme_autenticacion.models import Usuario
        
        # Validar que el destinatario existe
        if not Usuario.objects.filter(id=data['destinatario'].id).exists():
            raise serializers.ValidationError({
                'destinatario': 'Usuario destinatario no existe'
            })
        
        # Validar routing key
        routing_key = data.get('routing_key', '')
        if not routing_key.startswith('mensaje.usuario.'):
            raise serializers.ValidationError({
                'routing_key': 'Routing key debe comenzar con "mensaje.usuario."'
            })
        
        # Validar prioridad (1-3)
        prioridad = data.get('prioridad', 1)
        if prioridad not in [1, 2, 3]:
            raise serializers.ValidationError({
                'prioridad': 'Prioridad debe ser 1 (Baja), 2 (Media) o 3 (Alta)'
            })
        
        return data

class ActualizarEstadoMensajeSerializer(serializers.Serializer):
    """
    Serializer para actualizar estado de mensaje
    """
    estado = serializers.ChoiceField(
        choices=[
            (EstadoMensaje.LEIDO, 'Leído'),
            (EstadoMensaje.NO_LEIDO, 'No Leído'),
            (EstadoMensaje.ARCHIVADO, 'Archivado'),
            (EstadoMensaje.ELIMINADO, 'Eliminado'),
        ]
    )
    
    def validate_estado(self, value):
        """Validar estado"""
        estados_validos = [EstadoMensaje.LEIDO, EstadoMensaje.NO_LEIDO, 
                          EstadoMensaje.ARCHIVADO, EstadoMensaje.ELIMINADO]
        if value not in estados_validos:
            raise serializers.ValidationError(f"Estado inválido. Debe ser uno de: {estados_validos}")
        return value

class MarcarVariosLeidoSerializer(serializers.Serializer):
    """
    Serializer para marcar varios mensajes como leídos
    """
    mensaje_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        max_length=100
    )
    
    def validate_mensaje_ids(self, value):
        """Validar IDs de mensajes"""
        if not value:
            raise serializers.ValidationError("La lista no puede estar vacía")
        return value

class ConteoMensajesSerializer(serializers.Serializer):
    """
    Serializer para conteo de mensajes
    """
    total = serializers.IntegerField()
    no_leidos = serializers.IntegerField()
    por_estado = serializers.DictField(child=serializers.IntegerField())
    por_tipo = serializers.DictField(child=serializers.IntegerField())

class BuscarMensajesSerializer(serializers.Serializer):
    """
    Serializer para búsqueda de mensajes
    """
    query = serializers.CharField(max_length=100, min_length=3)
    limit = serializers.IntegerField(default=20, min_value=1, max_value=100)

#Serializador para los mensajes masivos con remitente
# Archivo: mensaje_serializer.py (agregar al final)

# En mensaje_serializer.py, modificar solo el CrearMensajeMultipleSerializer:

# En mensaje_serializer.py, modificar SOLO el CrearMensajeMultipleSerializer:

class CrearMensajeMultipleSerializer(serializers.Serializer):
    """
    Serializer para crear mensajes a múltiples destinatarios
    """
    destinatarios_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        max_length=50,
        help_text="Lista de IDs de destinatarios"
    )
    asunto = serializers.CharField(
        max_length=255, 
        required=False, 
        default="Sin asunto",
        help_text="Asunto del mensaje"
    )
    contenido = serializers.CharField(
        help_text="Contenido del mensaje"
    )
    tipo = serializers.ChoiceField(  # ← NUEVO CAMPO
        choices=TipoMensaje.choices,
        required=False,
        default=TipoMensaje.PRIVADO,
        help_text="Tipo de mensaje"
    )
    prioridad = serializers.IntegerField(
        min_value=1, 
        max_value=3, 
        default=1,
        help_text="Prioridad (1=baja, 2=media, 3=alta)"
    )
    metadata = serializers.DictField(
        required=False, 
        default=dict,
        help_text="Metadatos adicionales"
    )
    
    def validate_destinatarios_ids(self, value):
        """Validar que no haya duplicados"""
        if len(value) != len(set(value)):
            raise serializers.ValidationError("La lista de destinatarios contiene duplicados")
        return value
    
    def validate(self, data):
        """Validación personalizada"""
        from spme_autenticacion.models import Usuario
        
        # Verificar que todos los destinatarios existen
        destinatarios_existentes = Usuario.objects.filter(
            id__in=data['destinatarios_ids']
        ).count()
        
        if destinatarios_existentes != len(data['destinatarios_ids']):
            raise serializers.ValidationError({
                'destinatarios_ids': 'Uno o más destinatarios no existen en el sistema'
            })
        
        return data

class MensajesEnviadosSerializer(serializers.Serializer):
    """
    Serializer para la consulta de mensajes enviados
    """
    destinatario_id = serializers.IntegerField(
        required=False,
        help_text="Filtrar por destinatario específico"
    )
    tipo = serializers.ChoiceField(
        choices=TipoMensaje.choices,
        required=False,
        help_text="Filtrar por tipo de mensaje"
    )
    limit = serializers.IntegerField(
        min_value=1, 
        max_value=100, 
        default=50,
        help_text="Límite de resultados por página"
    )
    offset = serializers.IntegerField(
        min_value=0, 
        default=0,
        help_text="Offset para paginación"
    )