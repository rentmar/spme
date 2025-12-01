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
    codigo = models.CharField(max_length=50, blank=True, null=True)
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
        verbose_name='Objetivo especifico'
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
        blank=True,
        verbose_name='Objetivo Asociado'
    )

    class Meta:
        verbose_name = 'Indicador PEI'
        verbose_name_plural = 'Indicadores PEI'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.id}, {self.codigo} - {self.descripcion}"
    
#Indicador Cuantitativo
class IndicadorPeiCuantitativo(IndicadorPeiBase):
    TIPO_MEDICION = 'CUANTITATIVO'
    #tipo del inidicador
    tipo = models.CharField(max_length=20, default=TIPO_MEDICION, editable=False, verbose_name='Tipo del indicador')        
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
    TIPO_MEDICION = 'CUALITATIVO'

    #tipo del inidicador
    tipo = models.CharField(max_length=20, default=TIPO_MEDICION, editable=False, verbose_name='Tipo del Indicador')        
    #Atributos de Proporcion
    umbral_des_literal_um1 = models.TextField(blank=True, null=True)
    umbral_des_literal_um2 = models.TextField(blank=True, null=True)
    umbral_des_literal_um3 = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Indicador Cualitativo PEI'
        verbose_name_plural = 'Indicadores Cualitativos PEI'


#Actividad 
class ActividadPei(models.Model):
    ESTADOS_ACTIVIDAD = [
        ('CRD', 'Creada'),
        ('PLAN', 'Planificada'),
        ('RETR', 'Retraso'),
        ('REPROG', 'Reprogramacion'),
        ('EJEC', 'En Ejecucion'),
        ('REP', 'En Reporte'),
        ('FIN', 'Finalizado'),
    ]
    TIPO_ACTIVIDAD = [
        ('NODEF', 'No definido'),
        ('ACAP', 'Actividad de Capacitacion'),
        ('PRIN', 'Proyecto de Investigacion'),
        ('AOP', 'Actividad Operativa'),
        ('CSNS', 'Campaña de Sensibilizacion'),
        ('PDES', 'Proyecto de Desarrollo'),
        ('AINC', 'Actividad de Incidencia'),
        ('AART', 'Actividad de Articulacion'),
        ('OTRO', 'Otro'),
    ]
    #Datos de la actividad
    codigo = models.CharField(max_length=60, blank=True, null=True)

    nombreCorto = models.CharField(max_length=500, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)

    supuestos = models.TextField(null=True, blank=True)
    riesgos = models.TextField(null=True, blank=True)
    objetivo_de_actividad = models.TextField(null=True, blank=True) #Nuevo datos
    descripcion_evaluacion = models.TextField(null=True, blank=True) #Toda la informacion de la planificacion de la actividad
    descripcion_tipo_actividad = models.TextField(null=True, blank=True)

    #Tipo de la actividad
    tipo = models.ForeignKey(
        'spme_actividades.TipoActividad',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='actividades_pei',
        verbose_name='Tipo de Actividad'
    )

    #Fechas de la Actividad
    fecha_programada = models.DateField(null=True, blank=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_cierre = models.DateField(null=True, blank=True)

    #Presupuesto
    presupuesto = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    presupuestoGlobal = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    totalReportado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    totalEjecutado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    saldo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    gradoEjecucion = models.CharField(max_length=50, blank=True, null=True)
    procedencia_fondos = models.JSONField(null=True, blank=True)   
    #Estado de la actividad
    estado = models.CharField(max_length=15, choices=ESTADOS_ACTIVIDAD, default='CRD')
    
    #Pei
    pei = models.ForeignKey(
        Pei,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actividad_pei',
        verbose_name='Pei Al que pertenece la actividad'
    )

    #Responsable - CAMBIADO EL related_name
    responsable = models.ForeignKey(
        'spme_autenticacion.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actividades_pei_responsable',  
        verbose_name='Responsable de la actividad'
    )

    #Relaciones logicas con la estructura
    objetivos_pei = models.ManyToManyField(
        ObjetivoPei,
        related_name='actividades_relacionadas',
        verbose_name='Objetivos PEI relacionados'
    )
    factores_criticos = models.ManyToManyField(
        FactoresCriticos,
        related_name='actividades_factores_criticos',
        verbose_name='Factores Criticos relacionados'
    )    
    indicadores_cuantitativos = models.ManyToManyField(
        IndicadorPeiCuantitativo,
        related_name='actividades_cuantitativas',
        verbose_name='Indicadores cuantitativos relacionados'
    )
    indicadores_cualitativos = models.ManyToManyField(
        IndicadorPeiCualitativo,
        related_name='actividades_cualitativas',
        verbose_name='Indicadores cualitativas relacionados'
    )

    class Meta:
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'

    def __str__(self):
        return f'Actividad: {self.codigo}' 

#Tareas de la Actividad
class TareaActividadPei(models.Model):
    ESTADOS_TAREA = [
        ('PEN','Pendiente'),
        ('EPROG','En Progreso'),
        ('COMPL','Completada'),
    ]
    estado = models.CharField(max_length=15, choices=ESTADOS_TAREA, default='PEN')
    codigo = models.CharField(max_length=100, blank=True, null=True, unique=True)
    titulo = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_ejecucion = models.DateField(null=True, blank=True)
    fecha_creacion = models.DateField(null=True, blank=True)
    fecha_limite = models.DateField(null=True, blank=True)
    presupuestoDesglose = models.JSONField(null=True, blank=True)
    presupuesto = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    actividad = models.ForeignKey(
        ActividadPei,
        on_delete=models.CASCADE,
        related_name='tareas_pei',
        null=True,
        blank=True,
        verbose_name='Actividad Asociada'
    )

    class Meta:
        verbose_name='Tarea de Actividad PEI'
        verbose_name_plural='Tareas de Actividad PEI'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'{self.codigo} - {self.titulo or "Sin título"}'    



