from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from ..models import (
    SolicitudViaje, 
    InformeActividadPrincipal
    )


class VinculacionSolicitudInforme(models.Model):
    """
    Vinculación entre solicitudes de viaje e informes de actividad.
    
    REGLAS DE NEGOCIO:
    - Una solicitud NO puede tener más de una vinculación ACTIVA
    - Un informe puede tener múltiples solicitudes vinculadas
    - Se mantiene historial completo de vinculaciones

    RELACIONES:
    - solicitud: Referencia a SolicitudViaje (modelo existente)
    - informe: Referencia a InformeActividadPrincipal (modelo existente)
    - usuario_vinculo: Referencia a Usuario (modelo personalizado)
    """
    #Solicitud de viaje
    solicitud = models.ForeignKey(
        SolicitudViaje,
        on_delete=models.CASCADE,
        related_name='vinculaciones_informe',
        verbose_name="Solicitud de viaje"        
    )

    #Informe de Actividad Principal
    informe = models.ForeignKey(
        InformeActividadPrincipal,
        on_delete=models.CASCADE,
        related_name='vinculaciones_solicitudes',
        verbose_name='Informe de actividad principal'
    )

    #Fecha de vinculacion
    fecha_vinculacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de vinculacion'
    )

    #Usuario vinculo
    usuario_vinculo = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vinculaciones_realizadas',
        verbose_name='Usuario que vinculo el documento'
    )

    #Bandera de registro activo
    activa = models.BooleanField(
        default=True,
        verbose_name='Vinculacion activa',
        help_text='Indica si la vinculacion esta actualmente vigente'
    )

    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones'
    )

    class Meta:
        verbose_name = 'Vinculación Solicitud Viaje - Informe de Actividad'
        verbose_name_plural = 'Vinculaciones Solicitud Viaje - Informe de Actividad'
        unique_together = ['solicitud', 'informe']  # Evita duplicados
        ordering = ['-fecha_vinculacion']

    def __str__(self):
        estado = "✓" if self.activa else "✗"
        return f"{estado} {self.solicitud.numeroFormulario} → {self.informe.numeroInforme}"
    
    def save(self, *args, **kwargs):
        """
        Validación antes de guardar:
        No puede haber otra vinculación ACTIVA para la misma solicitud.
        """
        if self.activa:
            otras_activas = VinculacionSolicitudInforme.objects.filter(
                solicitud=self.solicitud,
                activa=True
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
        otra_activa = VinculacionSolicitudInforme.objects.filter(
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
