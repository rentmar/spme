from django.db import models
from spme_estructuracion_proyecto.models import(
    IndicadorObjetivoGeneral,
    IndicadorObjetivoEspecifico,
    IndicadorResultadoObjGral,
    IndicadorResultadoObjEspecifico
    )
from spme_monitoreo.models import InfActividad
from polymorphic.models import PolymorphicModel


class BitacoraIndicadorBase(PolymorphicModel):
    TIPOS_INDICADOR = [
        ('indicadorog', 'Indicador Objetivo General'),
        ('indicadoroe', 'Indicador Objetivo Específico'),
        ('indicadorrog', 'Indicador Resultado OG'),
        ('indicadorroe', 'Indicador Resultado OE'),
    ]
    
    TIPOS_DATO = [
        ('A-Z', 'Literal'),
        ('1-9', 'Numérico'),
        ('%', 'Porcentual'),
    ]
    
    tipo_indicador = models.CharField(max_length=15, choices=TIPOS_INDICADOR)
    tipo_dato = models.CharField(max_length=5, choices=TIPOS_DATO)
    id_indicador = models.IntegerField()
    
    # Campos para diferentes tipos de valores
    valor_literal = models.TextField(blank=True, null=True)
    valor_numerico = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    valor_porcentual = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    fecha_registro = models.DateField()
    observaciones = models.TextField(blank=True, null=True)
    archivos_adjuntos = models.JSONField(blank=True, null=True)
    timestamp_registro = models.DateTimeField(blank=True, null=True)
    
    informe_actividad = models.ForeignKey(
        InfActividad,
        on_delete=models.CASCADE,
        related_name='bitacoras_indicadores_base' 
    )
    
    snapshot_indicador = models.JSONField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Bitácora de Indicador Base'
        verbose_name_plural = 'Bitácoras de Indicadores Base'
        ordering = ['-fecha_registro', '-timestamp_registro']

# Modelos específicos con related_names únicos
class BitacoraIndicadorOG(BitacoraIndicadorBase):
    indicador_og = models.ForeignKey(
        IndicadorObjetivoGeneral,
        on_delete=models.CASCADE,
        related_name='bitacoras_og'  # Único para OG
    )
    
    class Meta:
        verbose_name = 'Bitácora Indicador OG'
        verbose_name_plural = 'Bitácoras Indicadores OG'

class BitacoraIndicadorOE(BitacoraIndicadorBase):
    indicador_oe = models.ForeignKey(
        IndicadorObjetivoEspecifico,
        on_delete=models.CASCADE,
        related_name='bitacoras_oe'  # Único para OE
    )
    
    class Meta:
        verbose_name = 'Bitácora Indicador OE'
        verbose_name_plural = 'Bitácoras Indicadores OE'

class BitacoraIndicadorROG(BitacoraIndicadorBase):
    indicador_rog = models.ForeignKey(
        IndicadorResultadoObjGral,
        on_delete=models.CASCADE,
        related_name='bitacoras_rog'  # Único para ROG
    )
    
    class Meta:
        verbose_name = 'Bitácora Indicador ROG'
        verbose_name_plural = 'Bitácoras Indicadores ROG'

class BitacoraIndicadorROE(BitacoraIndicadorBase):
    indicador_roe = models.ForeignKey(
        IndicadorResultadoObjEspecifico,
        on_delete=models.CASCADE,
        related_name='bitacoras_roe'  # Único para ROE
    )
    
    class Meta:
        verbose_name = 'Bitácora Indicador ROE'
        verbose_name_plural = 'Bitácoras Indicadores ROE'