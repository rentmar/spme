from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from polymorphic.models import PolymorphicModel
from spme_autenticacion.models import Usuario
from spme_monitoreo.models import InformeActividadPrincipal
from spme_monitoreo.models import InformeTareaPrincipal
from spme_monitoreo.models import (
    SolicitudFondos,
)
import random
import string
import uuid

# -------------------------------------------------------------------
# CLASE BASE PARA VALIDACIONES
# -------------------------------------------------------------------
class Validacion(PolymorphicModel):
    """
    Clase base polimórfica para validaciones de cualquier documento
    """
    # --- CÓDIGO DE SEGUIMIENTO ---
    codigoSeguimiento = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        help_text="Código único para seguimiento de la validación"
    )
    
    # --- QUIÉN VALIDA ---
    usuarioValidador = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='%(class)s_como_validador'
    )

    # --- QUIÉN CREÓ EL DOCUMENTO ---
    usuarioRedactor = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='%(class)s_como_redactor'
    )

    # --- ESTADO DE LA VALIDACIÓN (3 estados) ---
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
    ]

    estado = models.CharField(
        max_length=30,
        choices=ESTADOS,
        default='PENDIENTE'
    )
    
    comentarios = models.TextField(
        blank=True,
        help_text="Observaciones, sugerencias o justificación del voto"
    )

    # --- VERSIÓN DEL DOCUMENTO ---
    versionDocumento = models.CharField(
        max_length=10,
        default='1',
        help_text="Versión del documento al momento de validar"
    )

    # --- FECHAS ---
    fechaAsignacion = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha cuando se asignó la validación"
    )
    
    fechaResolucion = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha cuando se emitió el voto"
    )

    class Meta:
        ordering = ['-fechaAsignacion']
    
    def generar_codigo_unico(self):
        """Genera un código único para la validación"""
        from .models import ValidacionSolicitudFondos
        fecha = timezone.now().strftime('%Y%m%d')

        #Si es solicitud de fondos genera el codigo SF-FECHA-UID
        if isinstance(self, ValidacionSolicitudFondos):
            uid = uuid.uuid4().hex[:8].upper()
            return f"SF-{fecha}-{uid}"

        aleatorio = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"VAL-{fecha}-{aleatorio}"
    
    def save(self, *args, **kwargs):
        """
        - Genera código único si es nuevo
        - Actualiza fechaResolucion cuando cambia de pendiente
        - Registra historial siempre (creacion y cambio de estado)
        """
        from .models import HistorialValidacion

        #Detectar si es nuevo o existente
        is_new = not self.pk

        #Si es nuevo, guardar estado anterior como None
        if is_new:
            estado_anterior = None
        else:
            # Detectar cambio de estado para existentes
            try:
                original = Validacion.objects.get(pk=self.pk)
                estado_anterior = original.estado
            except Validacion.DoesNotExist:
                estado_anterior = None
        
        #Generar codigo si es nuevo
        if is_new and not self.codigoSeguimiento:
           self.codigoSeguimiento = self.generar_codigo_unico()
        
        # Actualizar fechaResolucion si cambia de pendiente
        if self.estado != 'PENDIENTE' and not self.fechaResolucion:
            self.fechaResolucion = timezone.now()

        # Guardar el registro
        super().save(*args, **kwargs)

        # 👇 REGISTRAR EN HISTORIAL SIEMPRE (creación O cambio)
        if is_new:
            # Caso 1: Es una NUEVA validación
            HistorialValidacion.objects.create(
                validacion=self,
                usuario=self.usuarioRedactor,  # El redactor es quien crea
                estado_anterior='Nueva Entrada',  # No había estado anterior
                estado_nuevo=self.estado,  # Casi siempre 'PENDIENTE'
                versionDocumento=self.versionDocumento,
                comentario=f"Validación creada - Estado inicial: {self.get_estado_display()}"
            )
        elif estado_anterior != self.estado:
            # Caso 2: Cambió el estado (APROBADO/RECHAZADO)
            usuario_cambio = self.usuarioValidador if self.estado != 'PENDIENTE' else self.usuarioRedactor
            HistorialValidacion.objects.create(
                validacion=self,
                usuario=usuario_cambio,
                estado_anterior=estado_anterior,
                estado_nuevo=self.estado,
                versionDocumento=self.versionDocumento,
                comentario=f"Cambio de estado: {estado_anterior} → {self.estado}"
            )    
        
    
    def __str__(self):
        return f"{self.codigoSeguimiento} - {self.usuarioValidador.username} - {self.estado}"


# -------------------------------------------------------------------
# VALIDACIÓN PARA INFORMES DE ACTIVIDAD
# -------------------------------------------------------------------
class ValidacionInformeActividad(Validacion):
    """
    Validación específica para Informes de Actividad Principal
    """
    informe = models.ForeignKey(
        InformeActividadPrincipal,
        on_delete=models.CASCADE,
        related_name='validaciones'
    )
    
    class Meta:
        # 🟢 SIN CONSTRAINTS - El error desaparece
        verbose_name = "Validación de Informe de Actividad"
        verbose_name_plural = "Validaciones de Informes de Actividad"
    
    def clean(self):
        """Validación a nivel de modelo para evitar duplicados"""
        if not self.pk:  # Solo para nuevas instancias
            existe = ValidacionInformeActividad.objects.filter(
                informe=self.informe,
                usuarioValidador=self.usuarioValidador
            ).exists()
            
            if existe:
                raise ValidationError(
                    f"Ya existe una validación para {self.usuarioValidador.username} "
                    f"en el informe {self.informe.numeroInforme}"
                )
    
    def save(self, *args, **kwargs):
        """Ejecutar validación antes de guardar"""
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"IA {self.informe.numeroInforme} - {self.codigoSeguimiento} - {self.estado}"


# -------------------------------------------------------------------
# VALIDACIÓN PARA INFORMES DE TAREA
# -------------------------------------------------------------------
class ValidacionInformeTarea(Validacion):
    """
    Validación específica para Informes de Tarea
    """
    informeTarea = models.ForeignKey(
        InformeTareaPrincipal,
        on_delete=models.CASCADE,
        related_name='validaciones'
    )
    
    class Meta:
        # 🟢 SIN CONSTRAINTS - El error desaparece
        verbose_name = "Validación de Informe de Tarea"
        verbose_name_plural = "Validaciones de Informes de Tarea"
    
    def clean(self):
        """Validación a nivel de modelo para evitar duplicados"""
        if not self.pk:  # Solo para nuevas instancias
            existe = ValidacionInformeTarea.objects.filter(
                informeTarea=self.informeTarea,
                usuarioValidador=self.usuarioValidador
            ).exists()
            
            if existe:
                raise ValidationError(
                    f"Ya existe una validación para {self.usuarioValidador.username} "
                    f"en el informe {self.informeTarea.numeroInforme}"
                )
    
    def save(self, *args, **kwargs):
        """Ejecutar validación antes de guardar"""
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"IT {self.informeTarea.numeroInforme} - {self.codigoSeguimiento} - {self.estado}"

# ===================================================================
# VALIDACIÓN PARA SOLICITUD DE FONDOS
# ===================================================================
class ValidacionSolicitudFondos(Validacion):
    """
    Validacion para solicitudes de fondos (actividades y tareas)
    """
    
    solicitud = models.ForeignKey(
        SolicitudFondos,
        on_delete=models.CASCADE,
        related_name='validaciones',
        verbose_name='Solicitud de Fondos'
    )

    class Meta:
        verbose_name = "Validación de Solicitud de Fondos"
        verbose_name_plural = "Validaciones de Solicitudes de Fondos"
        
    def save(self, *args, **kwargs):
        is_new = not self.pk
        if is_new and not self.codigoSeguimiento:
            self.codigoSeguimiento = self.generar_codigo_unico()
        self.clean()
        super().save(*args, **kwargs)
    
    def clean(self):
        if not self.pk:
            if ValidacionSolicitudFondos.objects.filter(
                solicitud=self.solicitud,
                usuarioValidador=self.usuarioValidador
            ).exists():
                raise ValidationError(
                    f"El usuario '{self.usuarioValidador.get_full_name()}' "
                    f"ya está asignado como validador para esta solicitud"
                )
    
    def __str__(self):
        codigo = self.solicitud.numeroFormulario or f"SF-{self.solicitud.id}"
        return f"💵 {codigo} - {self.codigoSeguimiento} - {self.get_estado_display()}"
    
    @property
    def tipo_solicitud(self):
        if self.solicitud.actividad_id and not self.solicitud.tarea_id:
            return 'ACTIVIDAD'
        elif self.solicitud.actividad_id and self.solicitud.tarea_id:
            return 'TAREA'
        return 'GENERAL'
        
    
    @property
    def monto_solicitud(self):
        return self.solicitud.montoSolicitado
    
    @property
    def codigo_solicitud(self):
        return self.solicitud.numeroFormulario or f"SF-{self.solicitud.id}"



# -------------------------------------------------------------------
# HISTORIAL DE CAMBIOS (TODAS LAS VALIDACIONES)
# -------------------------------------------------------------------
class HistorialValidacion(models.Model):
    """
    Historial de cambios en las validaciones (TODOS los tipos)
    """
    validacion = models.ForeignKey(
        Validacion,  # Clase base, acepta cualquier hija
        on_delete=models.CASCADE,
        related_name='historial'
    )
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='cambios_historial_validaciones'
    )
    
    estado_anterior = models.CharField(
        max_length=30,
        choices=Validacion.ESTADOS,
        blank=True
    )
    
    estado_nuevo = models.CharField(
        max_length=30,
        choices=Validacion.ESTADOS
    )
    
    versionDocumento = models.CharField(
        max_length=10,
        blank=True,
        help_text="Versión del documento al momento del cambio"
    )
    
    comentario = models.TextField(
        blank=True,
        help_text="Motivo del cambio o comentario adicional"
    )
    
    fechaCambio = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora en que ocurrió el cambio"
    )
    
    class Meta:
        verbose_name = "Historial de Validación"
        verbose_name_plural = "Historiales de Validaciones"
        ordering = ['-fechaCambio']
        indexes = [
            models.Index(fields=['validacion', 'fechaCambio']),
            models.Index(fields=['usuario', 'fechaCambio']),
            models.Index(fields=['estado_nuevo']),
        ]
    
    def __str__(self):
        if hasattr(self.validacion, 'informe'):
            tipo = "Actividad"
        elif hasattr(self.validacion, 'informeTarea'):
            tipo = "Tarea"
        elif hasattr(self.validacion, 'solicitud'):
            tipo = "Solicitud Fondos"
        else:
            tipo = "Desconocido"
        return f"{tipo} - {self.validacion.codigoSeguimiento} - {self.estado_anterior}→{self.estado_nuevo}"   
    # def __str__(self):
    #     tipo = "Actividad" if hasattr(self.validacion, 'informe') else "Tarea"
    #     return f"{tipo} - {self.validacion.codigoSeguimiento} - {self.estado_anterior}→{self.estado_nuevo}"
    
    