#spme_monitoreo/models/vinculacion_solicitud_informe_tarea.py
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
#modelo
from spme_monitoreo.models import (
    SolicitudViaje,
    InformeTareaPrincipal,
)

class VinculacionSolicitudInformeTarea(models.Model):
    """
    Vinculación entre solicitudes de viaje e informes de TAREA (Subactividad).

    REGLAS DE NEGOCIO:
    - Una solicitud NO puede tener más de una vinculación ACTIVA
    - Un informe puede tener múltiples solicitudes vinculadas
    - Se mantiene historial completo de vinculaciones

    RELACIONES:
    - solicitud: Referencia a SolicitudViaje (modelo existente)
    - informe: Referencia a InformeTareaPrincipal (modelo existente)
    - usuario_vinculo: Referencia a Usuario (modelo personalizado)
    """
    #Solicitud de viaje
    solicitud = models.ForeignKey(
        SolicitudViaje,
        on_delete=models.CASCADE,
        related_name="vinculaciones_informe_tarea",
        verbose_name="Solicitud de viaje tarea",
    )

    #Informe de tarea principal
    informe = models.ForeignKey(
        InformeTareaPrincipal,
        on_delete=models.CASCADE,
        related_name="vinculaciones_solicitudes_tarea",
        verbose_name="Informe de Tarea/Subactividad principal",
    )

    #Fecha de vinculacion
    fecha_vinculacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de vinculacion",
    )

    #Usuario vinculacion
    usuario_vinculo = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vinculaciones_realizadas_tarea",
        verbose_name="Usuario que vinculo el documento al informe de tarea",
    )

    #Bandera de vinculacion activa
    activa = models.BooleanField(
        default=True,
        verbose_name="Vinculacion activa",
        help_text="Indica si la vinculacion se encuentra o no vigente",
    )

    observaciones = models.TextField(
        null=True,
        blank=True,
        verbose_name="Observaciones",
    )

    datos_completos_vinculacion = models.JSONField(
        default=dict,
        verbose_name="Datos completos de la vinculacion"
    )

    class Meta:
        verbose_name = 'Vinculación Solicitud Viaje - Informe de Tarea/SubActividad'
        verbose_name_plural = 'Vinculaciones Solicitud Viaje - Informe de Tarea/SubActividad'
        unique_together = ['solicitud', 'informe']  # Evita duplicados
        ordering = ['-fecha_vinculacion']
    
    def __str__(self):
        estado = "✓" if self.activa else "✗"
        return f"{estado} {self.solicitud.numeroFormulario} → {self.informe.numeroInforme}"
    
    #Metodo de guardado
    def save(self, *args, **kwargs):
        """
        Validacion antes de guardado:
        No puede existir otra vinculacion ACTIVA para la solicitud
        """
        if self.activa:
            otras_activas = VinculacionSolicitudInformeTarea.objects.filter(
                solicitud = self.solicitud,
                activa = True
            ).exclude(pk=self.pk)

            if otras_activas.exists():
                otra = otras_activas.first()
                raise ValidationError({
                    'solicitud': ValidationError(
                        f"❌ La solicitud {self.solicitud.numeroFormulario} "
                        f"YA está vinculada al informe {otra.informe.numeroInforme}. "
                        f"Debe desvincularla primero."
                    )
                })
        
        super().save(*args, **kwargs)

    def desactivar(self):
        """Desactiva la vinculación actual"""
        self.activa = False
        self.save(update_fields=['activa'])
    
    def reactivar(self):
        """Reactivar una vinculación previamente desactivada"""
        otra_activa = VinculacionSolicitudInformeTarea.objects.filter(
            solicitud=self.solicitud,
            activa=True
        ).exclude(pk=self.pk).exists()
        
        if otra_activa:
            raise ValidationError(
                f"La solicitud {self.solicitud.numeroFormulario} ya tiene "
                "una vinculación activa con otro informe"
            )
        
        self.activa = True
        self.save(update_fields=['activa'])
