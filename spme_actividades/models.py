from django.db import models
from spme_estructuracion_proyecto.models import * 
from spme_estructuracion_pei.models import *
from spme_estructuracion_proyecto.models import Proyecto
from spme_autenticacion.models import Usuario


#Tipos de actividad
class TipoActividad(models.Model):
    sigla = models.CharField(max_length=20, null=True, blank=True)
    tipo_actividad = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Tipo de Actividad'
        verbose_name_plural = 'Tipos de Activida'

    def __str__(self):
        return f'{self.sigla} - {self.tipo_actividad}'    

#Actividad
class Actividad(models.Model):
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

    
    #Modificar
    tipo = models.ForeignKey(
        TipoActividad,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='actividades',
        verbose_name= 'Tipos de la actividad',
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

    #Procedencia de fondos (Viene de la planificacion):
    # "desglosePresupuesto": [
    #     {"id": 1, "nombre": "Fondos Propios", "monto": 100}, #Modelo ProcedenciaFondos 
    #     {"nombre": "Otro", "monto": 45, "manual": true},  #Dato Registrar
    #     {"id": 2, "nombre": "Financiador Uno", "monto": 45}
    # ] 
    procedencia_fondos = models.JSONField(null=True, blank=True)   

    #Estado de la actividad
    estado = models.CharField(max_length=15, choices=ESTADOS_ACTIVIDAD, default='CRD')

       #Usuario
    #responsable = models.CharField(max_length=255, blank=True, null=True) #Usuario Asignado

    # proceso = models.IntegerField()
    # resultado_og = models.IntegerField()
    # resultado_oe = models.IntegerField()
    # producto_oe = models.IntegerField()

    #Relaciones
    #Relaciones
    proceso = models.ForeignKey(
        Proceso,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actividad_proceso',
        verbose_name='Actividades relacionadas al Proceso',
        help_text='Actividades que se realizan para completar un proceso'
    )

    resultado_og = models.ForeignKey(
        ResultadoOG,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actividad_resultado_og',
        verbose_name='Actividades relacionadas al Resultado OG',
        help_text='Actividades realizadas para completar el Resultado OG'
    )

    resultado_oe = models.ForeignKey(
        ResultadoOE,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actividad_resultado_oe',
        verbose_name='Actividades relacionadas al Resultado OE',
        help_text='Actividades realizadas para completar el Resultado OE',
    )

    producto_oe = models.ForeignKey(
        ProductoOE,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actividad_producto_oe',
        verbose_name='Actividades relacionadas al Producto OE',
        help_text='Actividades realizadas para completar el Producto OE',
    )

    #pei_objetivo
    objetivo_pei = models.ForeignKey(
        ObjetivoPei,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actividades_objpei',
        verbose_name='Actividades que contribuyen al Producto OE',
        help_text='Actividades realizadas para completar el Obejtivo PEI'
    )
    #Indicador PEI
    indicador_pei = models.ForeignKey(
        IndicadorPeiBase,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actividades_indpei',
        verbose_name="Actividades relacionadas al Indicador PEI (cualitativo cuantitativo)",
        help_text="Actividades relacionadas al indicador cualitativo/cuantitativo PEI",
    )
    #Proyecto
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actividad_proyecto',
        verbose_name='Proyecto al que pertenece la actividad'
    )

    #Responsable
    responsable = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actividad_responsable',
        verbose_name='Responsable de la actividad'
    )

    # Ruta e indicadores
    rutaTrazadoIndicadores = models.JSONField(blank=True, null=True)
    # Factores criticos
    factoresCriticos = models.JSONField(blank=True, null=True)
    # estructura procedencia
    estructuraProcedencia = models.JSONField(blank=True, null=True)

    
    class Meta:
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'

    def __str__(self):
        return f'Actividad: {self.codigo}'    

    
    class Meta:
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'

    def __str__(self):
        return f'Actividad: {self.codigo}'    
    

#Tareas de la actividad
class TareaActividad(models.Model):
    ESTADOS_TAREA = [
        ('PEN','Pendiente'),
        ('EPROG','En Progreso'),
        ('COMPL','Completada'),
    ]
    estado = models.CharField(max_length=15, choices=ESTADOS_TAREA, default='PEN')
    titulo = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_limite = models.DateField(null=True, blank=True)
    presupuesto = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    #Relaciones
    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.SET_NULL,
        related_name='tareas',
        null=True,
        blank=True,
        verbose_name='Actividad asociada'
    )

    class Meta:
        verbose_name = 'Tarea de Actividad'
        verbose_name_plural = 'Tareas de Actividad'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'Tarea: {self.descripcion[:30]}... (Actividad: {self.actividad.codigo})'
