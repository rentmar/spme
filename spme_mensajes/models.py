# spme/spme_mensajes/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

Usuario = get_user_model()

#Tipo de mensaje
class TipoMensaje(models.TextChoices):
        PRIVADO = 'privado', 'Mensaje Privado'
        SISTEMA = 'sistema', 'Notificación del Sistema'
        ALERTA = 'alerta', 'Alerta Importante'
        RECORDATORIO = 'recordatorio', 'Recordatorio'
        REPROGRAMACION = 'reprogramacion', 'Reprogramación'
        RETRASO = 'retraso', 'Retraso de Actividad'
    
#Estado del mensaje
class EstadoMensaje(models.TextChoices):
        NO_LEIDO = 'no_leido', 'No Leído'
        LEIDO = 'leido', 'Leído'
        ARCHIVADO = 'archivado', 'Archivado'
        ELIMINADO = 'eliminado', 'Eliminado'    


class MensajeUsuario(models.Model):
        """
        MOdelo para los mensajes interno
        """
        #Informacion basica
        tipo = models.CharField(max_length=20, choices=TipoMensaje.choices, default=TipoMensaje.PRIVADO)
        #Usuarios
        remitente = models.ForeignKey(
                Usuario,
                on_delete=models.SET_NULL,
                related_name='mensajes_enviados',
                null=True,
                blank=True
        )
        destinatario = models.ForeignKey(
                Usuario,
                on_delete=models.CASCADE,
                related_name='mensajes_recibidos'                
        )
        #Contenido
        asunto = models.CharField(max_length=255)
        contenido = models.TextField()

        # Metadatos
        fecha_envio = models.DateTimeField(default=timezone.now, db_index=True)
        fecha_leido = models.DateTimeField(null=True, blank=True)
        estado = models.CharField(max_length=20, choices=EstadoMensaje.choices, default=EstadoMensaje.NO_LEIDO)
        
        # Relaciones
        actividad_id = models.IntegerField(null=True, blank=True, db_index=True)
        proyecto_id = models.IntegerField(null=True, blank=True, db_index=True)

        # Prioridad (1=baja, 2=media, 3=alta)
        prioridad = models.IntegerField(default=1)

        #Sistema
        message_id = models.CharField(max_length=100, unique=True, blank=True)

        # Campos adicionales para RabbitMQ/Celery
        routing_key = models.CharField(max_length=100, blank=True, db_index=True)
        metadata = models.JSONField(default=dict, blank=True)
        referencia_id = models.CharField(max_length=100, blank=True, db_index=True)

        # Fecha de expiración (opcional)
        fecha_expiracion = models.DateTimeField(null=True, blank=True)
        fecha_actualizacion = models.DateTimeField(auto_now=True)

        # Icono para UI (emoji o nombre de icono)
        icono = models.CharField(
            max_length=20, 
            default='📧',  # Emoji por defecto
            blank=True,
            help_text="Emoji o nombre de icono para la UI"
        )
        
        # Acción asociada (botón en la UI)
        accion_url = models.URLField(
            max_length=500, 
            blank=True, 
            null=True,
            help_text="URL para acción asociada al mensaje"
        )
        
        accion_texto = models.CharField(
            max_length=100, 
            blank=True, 
            null=True,
            help_text="Texto del botón de acción"
        )

        class Meta:
            verbose_name = 'Mensaje de Usuario'
            verbose_name_plural = 'Mensajes de Usuarios'
            ordering = ['-fecha_envio', '-prioridad']
            indexes = [
                models.Index(fields=['destinatario', 'estado', 'fecha_envio']),
                models.Index(fields=['destinatario', 'tipo', 'fecha_envio']),
                models.Index(fields=['fecha_envio']),
                models.Index(fields=['actividad_id', 'tipo']),
                models.Index(fields=['proyecto_id', 'tipo']),
                models.Index(fields=['routing_key', 'fecha_envio']),
            ]

        def __str__(self):
            return f"{self.asunto} - {self.destinatario.username}"
        
        def save(self, *args, **kwargs):
            """Generar message_id automáticamente si no existe"""
            if not self.message_id:
                self.message_id = f"MSG-{uuid.uuid4().hex[:12].upper()}"
            super().save(*args, **kwargs)

    
        def marcar_como_leido(self, commit=True):
            """Marca el mensaje como leído"""
            if self.estado == EstadoMensaje.NO_LEIDO:
                self.estado = EstadoMensaje.LEIDO
                self.fecha_leido = timezone.now()
                if commit:
                    self.save(update_fields=['estado', 'fecha_leido', 'fecha_actualizacion'])
            return self
        
        def marcar_como_no_leido(self, commit=True):
            """Marca el mensaje como no leído"""
            if self.estado == EstadoMensaje.LEIDO:
                self.estado = EstadoMensaje.NO_LEIDO
                self.fecha_leido = None
                if commit:
                    self.save(update_fields=['estado', 'fecha_leido', 'fecha_actualizacion'])
            return self
        
        def archivar(self, commit=True):
            """Archiva el mensaje"""
            self.estado = EstadoMensaje.ARCHIVADO
            if commit:
                self.save(update_fields=['estado', 'fecha_actualizacion'])
            return self
    
        def eliminar(self, commit=True):
            """Marca el mensaje como eliminado (soft delete)"""
            self.estado = EstadoMensaje.ELIMINADO
            if commit:
                self.save(update_fields=['estado', 'fecha_actualizacion'])
            return self

        @property
        def es_leido(self):
            return self.estado == EstadoMensaje.LEIDO
        
        @property
        def es_urgente(self):
            return self.prioridad >= 3
        
        @property
        def es_expirado(self):
            """Verifica si el mensaje ha expirado"""
            if self.fecha_expiracion:
                return timezone.now() > self.fecha_expiracion
            return False
        
        @property
        def tiene_accion(self):
            """Verifica si el mensaje tiene acción asociada"""
            return bool(self.accion_url and self.accion_texto)
        
        def obtener_datos_contexto(self):
            """Obtiene datos para serialización"""
            return {
                'id': self.pk,
                'message_id': self.message_id,
                'tipo': self.tipo,
                'tipo_display': self.get_tipo_display(),
                'asunto': self.asunto,
                'contenido': self.contenido,
                'estado': self.estado,
                'estado_display': self.get_estado_display(),
                'prioridad': self.prioridad,
                'fecha_envio': self.fecha_envio,
                'fecha_leido': self.fecha_leido,
                'fecha_expiracion': self.fecha_expiracion,
                'es_leido': self.es_leido,
                'es_urgente': self.es_urgente,
                'es_expirado': self.es_expirado,
                'tiene_accion': self.tiene_accion,
                'accion_url': self.accion_url,
                'accion_texto': self.accion_texto,
                'icono': self.icono,
                'actividad_id': self.actividad_id,
                'proyecto_id': self.proyecto_id,
                'metadata': self.metadata,
                'referencia_id': self.referencia_id,
                'remitente': {
                    'id': self.remitente.pk if self.remitente else None,
                    'username': self.remitente.username if self.remitente else 'Sistema',
                    'nombre_completo': self.remitente.get_full_name() if self.remitente else 'Sistema',
                } if self.remitente else {
                    'id': None,
                    'username': 'Sistema',
                    'nombre_completo': 'Sistema',
                },
                'destinatario': {
                    'id': self.destinatario.pk,
                    'username': self.destinatario.username,
                    'nombre_completo': self.destinatario.get_full_name(),
                }
            }
        