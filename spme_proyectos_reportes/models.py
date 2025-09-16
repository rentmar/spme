from django.db import models
from spme_estructuracion_proyecto.models import(
    IndicadorObjetivoGeneral,
    IndicadorObjetivoEspecifico,
    IndicadorResultadoObjGral,
    IndicadorResultadoObjEspecifico
    )

# Modelo para la bitacora
class BitacoraIndicador(models.Model):
    fechaBitacora = models.DateField(blank=True, null=True)
    cantidadAvance = models.CharField(max_length=100, blank=True, null=True)
    reporteEscrito = models.TextField(null=True, blank=True)
    linkSubida = models.TextField(null=True, blank=True)
    tipoIndicador = models.CharField(max_length=100, blank=True, null=True)
    
    # Relación con el modelo base de indicadores (puede ser cualquier tipo)
    # indicador = models.ForeignKey(
    #     IndicadorProyecto,
    #     on_delete=models.CASCADE,
    #     related_name='bitacoras',
    #     verbose_name='Indicador asociado'
    # )

    #Relacion a Indicador OG
    indicadorog = models.ForeignKey(
        IndicadorObjetivoGeneral,
        on_delete=models.SET_NULL,  
        related_name='bitacoras_indicadorog',
        null=True,
        blank=True
    )

    #Relacion al Indicador OE
    indicadoroe = models.ForeignKey(
        IndicadorObjetivoEspecifico,
        on_delete=models.SET_NULL,
        related_name='bitacoras_indicadoroe',
        null=True,
        blank=True
    )

    #Relacion al Indicador Resultado  de OG
    indicadorrog = models.ForeignKey(
        IndicadorResultadoObjGral,
        on_delete=models.SET_NULL,
        related_name='bitacoras_indicadorrog',
        null=True,
        blank=True,
    )

    #Relacion al indicador Resultado de OE
    indicadorroe = models.ForeignKey(
        IndicadorResultadoObjEspecifico,
        on_delete=models.SET_NULL,
        related_name='bitacoras_indicadorroe',
        null=True,
        blank=True,
    )   
    
    class Meta:
        verbose_name = 'Bitácora de Indicador'
        verbose_name_plural = 'Bitácoras de Indicadores'
    
    def __str__(self):
        return f"Bitácora - {self.fechaBitacora} - {self.indicador.codigo}"
    
   
   