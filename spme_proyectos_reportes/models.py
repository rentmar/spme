from django.db import models
from spme_estructuracion_proyecto.models import(
    IndicadorObjetivoGeneral,
    IndicadorObjetivoEspecifico,
    IndicadorResultadoObjGral,
    IndicadorResultadoObjEspecifico
    )
from spme_monitoreo.models import InfActividad, InfTarea
from polymorphic.models import PolymorphicModel
#informe Actividad/Subactividad principal
from spme_monitoreo.models import (
    InformeActividadPrincipal,
    InformeTareaPrincipal,
)
from spme_autenticacion.models import Usuario

#############################  Bitacora Informes Sub ACT/SUBACT   ############################
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
    #timestamp_registro = models.DateTimeField(blank=True, null=True)
    # --- CAMPOS DE SEGUIMIENTO (TIMESTAMPS) ---
    timestamp_registro = models.DateTimeField(
        auto_now_add=True,  # Se establece automáticamente al crear
        verbose_name='Fecha y hora de registro',
        help_text='Fecha y hora en que se creó el registro',
        blank=True, 
        null=True
    )
    timestamp_ultima_modificacion = models.DateTimeField(
        auto_now=True,  # Se actualiza automáticamente al guardar
        verbose_name='Última modificación',
        help_text='Fecha y hora de la última modificación',
        blank=True,
        null=True
    )


    #Informe de Actividad
    informe_actividad = models.ForeignKey(
        InfActividad,
        on_delete=models.CASCADE,
        related_name='bitacoras_indicadores_base',
        blank=True,
        null=True,
        verbose_name='Informe de Actividad'
    )

    #Informe de Tarea/Subactividad
    informe_tarea = models.ForeignKey(
        InfTarea,
        on_delete=models.CASCADE,
        related_name='bitacoras_tarea_indicadores',
        blank=True,
        null=True,
        verbose_name='Informe de Tarea',
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

####################### BITACORAS INFORME ACTIVIDAD/SUBACTIVIDAD PRINCIPAL ###################

class BitacoraPrincipalIndicadorBase(PolymorphicModel):
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

    # Campos para diferentes tipos de valores
    valor_literal = models.TextField(blank=True, null=True)
    valor_numerico = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    valor_porcentual = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    fecha_registro = models.DateField()
    observaciones = models.TextField(blank=True, null=True)
    archivos_adjuntos = models.JSONField(blank=True, null=True)

    #Usuario que registra
    usuario_registro = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL, 
        related_name='bitacoras_indicador_usuario',
        blank=True,
        null=True,
        verbose_name='Usuario que registro',
        help_text='Usuario que realizó el registro en la bitacora'
    )

    # --- CAMPOS DE SEGUIMIENTO (TIMESTAMPS) ---
    timestamp_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha y hora de registro',
        help_text='Fecha y hora en que se creó el registro',
        blank=True, 
        null=True
    )
    timestamp_ultima_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última modificación',
        help_text='Fecha y hora de la última modificación',
        blank=True,
        null=True
    )

    snapshot_indicador = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name = 'Bitácora Principal de Indicador Base'
        verbose_name_plural = 'Bitácora Principal de Indicadores Base'
        ordering = ['-fecha_registro', '-timestamp_registro']

#Modelos especificos con relaciones

#Bitacoras para Indicadorog
class BitacoraPrincipalIndicadorOg(BitacoraPrincipalIndicadorBase):
    #Relacion con el indicador og
    indicador_og = models.ForeignKey(
        IndicadorObjetivoGeneral,
        on_delete=models.CASCADE,
        related_name='bitacoras_og_principal_indicador',
    )
    #Relacion con el informe de actividad, que realizo el registro
    informe_actividad = models.ForeignKey(
        InformeActividadPrincipal,  
        on_delete=models.CASCADE,
        related_name='bitacoras_og_principal_informe_actividad', 
        blank=True,
        null=True,
        verbose_name='Informe de Actividad (OG)'
    )
    #Relacion con el informe de tarea, que realizo el registro
    informe_tarea = models.ForeignKey(
        InformeTareaPrincipal,  # Ajusta el import
        on_delete=models.CASCADE,
        related_name='bitacoras_og_tarea_principal_informe_tarea',  # ← related name exclusivo
        blank=True,
        null=True,
        verbose_name='Informe de Tarea (OG)'
    )

    class Meta:
        verbose_name = 'Bitacora Principal Indicador OG'
        verbose_name_plural = 'Bitacoras Principal de Indicador OG'

#Bitacoras para indicador oe
class BitacoraPrincipalIndicadorOE(BitacoraPrincipalIndicadorBase):
    indicador_oe = models.ForeignKey(
        IndicadorObjetivoEspecifico,
        on_delete=models.CASCADE,
        related_name='bitacoras_oe_principal_indicador'
    )
    
    #Relaciones informe actividad
    informe_actividad = models.ForeignKey(
        InformeActividadPrincipal,
        on_delete=models.CASCADE,
        related_name='bitacoras_oe_principal_informe_actividad', 
        blank=True,
        null=True,
        verbose_name='Informe de Actividad (OE)'
    )
    #Relaciones informe subactividad
    informe_tarea = models.ForeignKey(
        InformeTareaPrincipal,
        on_delete=models.CASCADE,
        related_name='bitacoras_oe_tarea_principal_informe_tarea',  # ← exclusivo
        blank=True,
        null=True,
        verbose_name='Informe de Tarea (OE)'
    )
    
    class Meta:
        verbose_name = 'Bitacora Principal Indicador OE'
        verbose_name_plural = 'Bitacoras Principal Indicadores OE'

#Bitacoras para indicadores rog
class BitacoraPrincipalIndicadorRog(BitacoraPrincipalIndicadorBase):
    #indicador
    indicador_rog = models.ForeignKey(
        IndicadorResultadoObjGral,
        on_delete=models.CASCADE,
        related_name='bitacoras_rog_principal'
    )        
    #Relacion al informe de actividad
    informe_actividad = models.ForeignKey(
        InformeActividadPrincipal,
        on_delete=models.CASCADE,
        related_name='bitacoras_rog_principal_informe_actividad',
        blank=True,
        null=True,
        verbose_name='Informe de Actividad (ROG)'
    )
    #Relacion al informe de tarea
    informe_tarea = models.ForeignKey(
        InformeTareaPrincipal,
        on_delete=models.CASCADE,
        related_name='bitacoras_rog_tarea_principal_informe_tarea', 
        blank=True,
        null=True,
        verbose_name='Informe de Tarea (ROG)'
    )

    class Meta:
        verbose_name = 'Bitacora Principal Indicador ROG'
        verbose_name_plural = 'Bitacoras Principal Indicadores ROG'

#Bitacoras indicador ROE
class BitacoraPrincipalIndicadorRoe(BitacoraPrincipalIndicadorBase):
    #indicador
    indicador_roe = models.ForeignKey(
        IndicadorResultadoObjEspecifico,
        on_delete=models.CASCADE,
        related_name='bitacoras_roe_principal'
    )
    #Relacion al informe de actividad, 
    informe_actividad = models.ForeignKey(
        InformeActividadPrincipal,
        on_delete=models.CASCADE,
        related_name='bitacoras_roe_principal_informe_actividad',  
        blank=True,
        null=True,
        verbose_name='Informe de Actividad (ROE)'
    )
    #Relacion al informe de tarea, que realizo el registro
    informe_tarea = models.ForeignKey(
        InformeTareaPrincipal,
        on_delete=models.CASCADE,
        related_name='bitacoras_roe_tarea_principal_informe_tarea',
        blank=True,
        null=True,
        verbose_name='Informe de Tarea (ROE)'
    )
    class Meta:
        verbose_name = 'Bitacora Principal Indicador ROE'
        verbose_name_plural = 'Bitacoras Principal Indicadores ROE'