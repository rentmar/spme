from django.db import models
from spme_estructuracion_proyecto.models import IndicadorProyecto

# Modelo para la bitacora
class BitacoraIndicador(models.Model):
    fechaBitacora = models.DateField(blank=True, null=True)
    cantidadAvance = models.CharField(max_length=100, blank=True, null=True)
    reporteEscrito = models.TextField(null=True, blank=True)
    linkSubida = models.TextField(null=True, blank=True)
    tipoIndicador = models.CharField(max_length=100, blank=True, null=True)
    
    # Relación con el modelo base de indicadores (puede ser cualquier tipo)
    indicador = models.ForeignKey(
        IndicadorProyecto,
        on_delete=models.CASCADE,
        related_name='bitacoras',
        verbose_name='Indicador asociado'
    )
    
    class Meta:
        verbose_name = 'Bitácora de Indicador'
        verbose_name_plural = 'Bitácoras de Indicadores'
    
    def __str__(self):
        return f"Bitácora - {self.fechaBitacora} - {self.indicador.codigo}"
    
    def save(self, *args, **kwargs):
        # Auto-completar el tipo de indicador basado en el tipo concreto
        if self.indicador:
            # Obtener el tipo concreto del indicador (subclase)
            if hasattr(self.indicador, 'indicadorobjetivogeneral'):
                self.tipoIndicador = 'Indicador Objetivo General'
            elif hasattr(self.indicador, 'indicadorresultadoobjgral'):
                self.tipoIndicador = 'Indicador Resultado OG'
            elif hasattr(self.indicador, 'indicadorobjetivoespecifico'):
                self.tipoIndicador = 'Indicador Objetivo Específico'
            elif hasattr(self.indicador, 'indicadorresultadoobjespecifico'):
                self.tipoIndicador = 'Indicador Resultado OE'
            else:
                self.tipoIndicador = 'Indicador de Proyecto'
        super().save(*args, **kwargs) 
