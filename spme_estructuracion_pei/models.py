from django.db import models
from django.utils import timezone
from polymorphic.models import PolymorphicModel

class EstructuraPei(models.Model):
    id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=50, verbose_name='tiulo')
    descripcion = models.TextField(max_length=250,verbose_name='descripcion', blank=False, null=False)
    fecha_creacion = models.DateTimeField(verbose_name='fecha_creacion')
    fecha_inicio = models.DateField(verbose_name='fecha_inicio')
    fecha_fin = models.DateField(verbose_name='fecha_fin')
    esta_vigente = models.BooleanField(verbose_name='esta_vigente')
    creado_el = models.DateTimeField(verbose_name='creado_el')
    modificado_el = models.DateTimeField(verbose_name='modificado_el')

    def __str__(self):
        return self.titulo

    class Meta:
        db_table = 'spme_estructuracion_pei'
        verbose_name = 'Estructuracion_pei'
        verbose_name_plural = 'No definidos'

####################### PEI ##########################################
class Pei(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_inicio = models.DateField(default=timezone.now, null=True, blank=True)
    fecha_fin = models.DateField(default=timezone.now, null=True, blank=True)
    esta_vigente = models.BooleanField(default=False)

    creado_el = models.DateTimeField(auto_now_add=True)
    modificado_el = models.DateTimeField(auto_now=True)

    class Meta:  
        verbose_name = 'PEI'
        verbose_name_plural = 'PEIs'
        ordering = ['titulo']  

    def __str__(self):
        return self.titulo



#ObjetivoGeneralPei
class ObjetivoPei(models.Model):
    codigo = models.CharField(max_length=50, blank=True, null=True)
    descripcion = models.TextField()
    pei = models.ForeignKey(
        Pei, 
        on_delete=models.CASCADE, 
        related_name='pei_obj_general')
    
    creado_el = models.DateTimeField(auto_now_add=True)
    modificado_el = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Objetivo General PEI'
        verbose_name_plural = 'Objetivos Generales PEI'

    def __str__(self):
        return self.codigo


#Factores criticos
class FactoresCriticos(models.Model):
    factor_critico = models.TextField(null=True, blank=True)
    #Relaciones
    objetivo_especifico = models.ForeignKey(
        ObjetivoPei,
        on_delete=models.SET_NULL,
        related_name='factores_criticos',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Factor critico'
        verbose_name_plural = 'Factores criticos'

    def __str__(self):
        return self.factor_critico    




# Indicadores del PEI
class IndicadorPeiBase(PolymorphicModel):
    codigo = models.CharField(max_length=50, null=True, blank=True)
    descripcion = models.TextField(verbose_name='Indicador')
    captura_informacion = models.TextField(blank=True, null=True)
    responsabilidad = models.CharField(max_length=255, blank=True, null=True)
    frecuencia_recopilacion = models.CharField(max_length=255, blank=True, null=True)
    uso_informacion = models.TextField(blank=True, null=True)
    
    #Fechas
    creado_el = models.DateTimeField(auto_now_add=True)
    modificado_el = models.DateTimeField(auto_now=True)

    #Relacion al objetivo
    objetivo = models.ForeignKey(
        ObjetivoPei, 
        on_delete=models.CASCADE,
        related_name='indicador_pei_objetivo',
        null=True,
        blank=True
    )

    #Relacion al Pei
    """
    pei = models.ForeignKey(
        Pei,
        on_delete=models.CASCADE,
        related_name='indicador_pei_pei',
        null=True,
        blank=True,
    )
    """


    class Meta:
        verbose_name = 'Indicador PEI'
        verbose_name_plural = 'Indicadores PEI'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.id}, {self.codigo} - {self.descripcion}"
    
#Indicador Cuantitativo
class IndicadorPeiCuantitativo(IndicadorPeiBase):
    TIPO_MEDICION = 'Proporcion'
    #tipo del inidicador
    tipo = models.CharField(max_length=20, default=TIPO_MEDICION, editable=False, verbose_name='Tipo')        
    #Atributos de Proporcion
    numerador = models.TextField(blank=True, null=True)
    denominador = models.TextField(blank=True, null=True)
    umbral_des_numeral = models.IntegerField(blank=True, null=True)
    umbral_des_literal_um1 = models.TextField(blank=True, null=True)
    umbral_des_literal_um2 = models.TextField(blank=True, null=True)
    umbral_des_literal_um3 = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Indicador Cuantitativo PEI'
        verbose_name_plural = 'Indicadores Cuantitativos PEI'

#Indicador cualitativo, señal de avance
class IndicadorPeiCualitativo(IndicadorPeiBase):
    TIPO_MEDICION = 'Avance'

    #tipo del inidicador
    tipo = models.CharField(max_length=20, default=TIPO_MEDICION, editable=False, verbose_name='Tipo')        
    #Atributos de Proporcion
    umbral_des_literal_um1 = models.TextField(blank=True, null=True)
    umbral_des_literal_um2 = models.TextField(blank=True, null=True)
    umbral_des_literal_um3 = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Indicador Cualitativo PEI'
        verbose_name_plural = 'Indicadores Cualitativos PEI'
