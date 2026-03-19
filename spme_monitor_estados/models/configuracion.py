# spme_monitor_estados/models/configuracion.py
# Propósito: Almacena la configuración para cada tipo de entidad
# Se gestiona completamente desde el admin de Django

from django.db import models

class ConfiguracionMonitoreo(models.Model):
    """
    Configuración para cada tipo de entidad monitoreada
    """
    
    # Tipos de entidad disponibles
    TIPO_ENTIDAD = [
        ('actividad', 'Actividad'),
        ('tarea', 'Tarea'),
        ('actividad_pei', 'Actividad PEI'),
        ('tarea_pei', 'Tarea PEI'),
    ]
    
    # Niveles de prioridad para emails
    PRIORIDAD = [
        (1, 'Baja'),
        (2, 'Media'),
        (3, 'Alta'),
        (4, 'Crítica'),
    ]
    
    # Identificación de la entidad
    tipo_entidad = models.CharField(
        max_length=20,
        choices=TIPO_ENTIDAD,
        unique=True,  # Solo una configuración por tipo
        verbose_name="Tipo de Entidad"
    )
    
    descripcion = models.CharField(
        max_length=200,
        blank=True,
        help_text="Descripción del monitoreo"
    )
    
    # Control de activación
    activo = models.BooleanField(
        default=True,
        verbose_name="Monitoreo activo"
    )
    
    # Configuración de prioridad para emails
    prioridad_notificacion = models.IntegerField(
        choices=PRIORIDAD,
        default=2,
        verbose_name="Prioridad de notificación",
        help_text="Determina el lote de envío de emails (más alto = más rápido)"
    )
    
    # Umbrales de tiempo para retrasos
    umbral_retraso_leve = models.PositiveIntegerField(
        default=3,
        verbose_name="Días para retraso leve"
    )
    
    umbral_retraso_critico = models.PositiveIntegerField(
        default=15,
        verbose_name="Días para retraso crítico"
    )
    
    # Control de tipos de notificación
    notificaciones_internas = models.BooleanField(
        default=True,
        verbose_name="Notificaciones internas",
        help_text="Enviar mensajes a la bandeja del usuario"
    )
    
    notificaciones_email = models.BooleanField(
        default=True,
        verbose_name="Notificaciones por email",
        help_text="Enviar correos electrónicos (procesados por lotes)"
    )
    
    # Metadata
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuración de Monitoreo"
        verbose_name_plural = "Configuraciones de Monitoreo"
        ordering = ['-prioridad_notificacion', 'tipo_entidad']
    
    def __str__(self):
        return f"{self.get_tipo_entidad_display()} - {self.get_prioridad_notificacion_display()}"