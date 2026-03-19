# spme_monitor_estados/models/cola_email.py
# Propósito: Almacena emails pendientes de envío
# Permite procesamiento por lotes y reintentos

from django.db import models
from django.utils import timezone
from datetime import timedelta


class EmailEnCola(models.Model):
    """
    Modelo para encolar emails antes de enviar
    Permite procesamiento por lotes y reintentos automáticos
    """
    # Estados posibles del email
    ESTADO = [
        ('pendiente', 'Pendiente'),  # Esperando ser enviado
        ('enviado', 'Enviado'),      # Enviado exitosamente
        ('error', 'Error'),           # Falló el envío
        ('cancelado', 'Cancelado'),   # Cancelado manualmente
    ]

    # Prioridades (coinciden con las de configuración)
    PRIORIDAD = [
        (1, 'Baja'),
        (2, 'Media'),
        (3, 'Alta'),
        (4, 'Crítica'),
    ]

    # ============================================================
    # Datos del destinatario
    # ============================================================
    destinatario = models.EmailField(
        db_index=True,
        help_text="Email del destinatario principal"
    )

    copia = models.JSONField(
        default=list,
        blank=True,
        help_text="Lista de emails en copia (CC)"
    )

    copia_oculta = models.JSONField(
        default=list,
        blank=True,
        help_text="Lista de emails en copia oculta (BCC)"
    )

    # ============================================================
    # Contenido del email
    # ============================================================
    asunto = models.CharField(
        max_length=255,
        help_text="Asunto del email"
    )

    cuerpo_html = models.TextField(
        help_text="Versión HTML del email (con estilos)"
    )

    cuerpo_texto = models.TextField(
        blank=True,
        help_text="Versión texto plano (alternativa)"
    )

    # ============================================================
    # Metadatos de control
    # ============================================================
    prioridad = models.IntegerField(
        choices=PRIORIDAD,
        default=2,
        db_index=True,
        help_text="Prioridad del email (determina orden de envío)"
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO,
        default='pendiente',
        db_index=True,
        help_text="Estado actual del email"
    )

    # Contexto para tracking (saber qué generó este email)
    tipo_entidad = models.CharField(
        max_length=50,
        blank=True,
        help_text="Tipo de entidad que generó el email (actividad, tarea, etc.)"
    )

    entidad_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="ID de la entidad relacionada"
    )

    evento = models.CharField(
        max_length=50,
        blank=True,
        help_text="Evento que generó la notificación"
    )

    # ============================================================
    # Control de tiempo
    # ============================================================
    creado_en = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Fecha y hora de creación"
    )
    
    programado_para = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="Fecha y hora programada para envío (según prioridad)"
    )
    
    enviado_en = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha y hora real de envío"
    )

    # ============================================================
    # Control de reintentos
    # ============================================================
    intentos = models.PositiveIntegerField(
        default=0,
        help_text="Número de intentos realizados"
    )
    
    error = models.TextField(
        blank=True,
        help_text="Mensaje de error si falló el envío"
    )

    class Meta:
        verbose_name = "Email en Cola"
        verbose_name_plural = "Emails en Cola"
        indexes = [
            # Índice compuesto para búsquedas eficientes de lotes
            models.Index(fields=['estado', 'prioridad', 'programado_para']),
            models.Index(fields=['estado', 'creado_en']),
        ]
        ordering = ['-prioridad', 'programado_para']
    
    def __str__(self):
        return f"{self.asunto} - {self.destinatario} ({self.get_estado_display()})"
    
    def marcar_enviado(self):
        """
        Marca el email como enviado exitosamente
        """
        self.estado = 'enviado'
        self.enviado_en = timezone.now()
        self.save(update_fields=['estado', 'enviado_en'])
    
    def marcar_error(self, error_msg):
        """
        Marca el email como error y programa reintento si corresponde
        """
        self.estado = 'error'
        self.error = error_msg
        self.intentos += 1
        
        # Si ha fallado menos de 3 veces, programar reintento
        if self.intentos < 3:
            self.estado = 'pendiente'  # Vuelve a pendiente para reintentar
            # Espera progresiva: 10min, 20min, 30min
            self.programado_para = timezone.now() + timedelta(minutes=10 * self.intentos)
        
        self.save(update_fields=['estado', 'error', 'intentos', 'programado_para'])
    
    @classmethod
    def obtener_lote(cls, limite=25, prioridad_minima=1):
        """
        Obtiene un lote de emails pendientes para enviar
        
        Args:
            limite: Máximo número de emails a obtener
            prioridad_minima: Prioridad mínima a incluir (1-4)
        
        Returns:
            QuerySet con los emails a procesar
        """
        return cls.objects.filter(
            estado='pendiente',
            programado_para__lte=timezone.now(),  # Solo los que ya deben enviarse
            prioridad__gte=prioridad_minima
        ).order_by('-prioridad', 'programado_para')[:limite]