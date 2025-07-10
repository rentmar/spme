from django.db import models

# Create your models here.
#Actividad
class Actividad(models.Model):
    ESTADOS_ACTIVIDAD = [
        ('SPLAN', 'Sin Planificar'),
        ('PLAN', 'Planificado'),
        ('EJEC', 'En Ejecución'),
        ('POST', 'Postergado'),
        ('CANC', 'Cancelado'),
        ('COMP', 'Completado'),
    ]
    PROCEDENCIA_FONDOS = [
        ('UG', 'Fondos de la Institucion'),
        ('PROY', 'Fondos del proyecto'),
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
    ]
    codigo = models.CharField(max_length=60, blank=True, null=True)
    descripcion = models.TextField(null=True, blank=True)
    tipo = models.CharField(max_length=30, choices=TIPO_ACTIVIDAD, default='NODEF')
    fecha_programada = models.DateField(null=True, blank=True)
    duracion = models.IntegerField(null=True, blank=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_cierre = models.DateField(null=True, blank=True)
    #Presupuesto
    presupuesto = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    #Forndo de PEI
    presupuesto_pei = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    #Estado de la actividad
    estado = models.CharField(max_length=15, choices=ESTADOS_ACTIVIDAD, default='SPLAN')

    #Seleccion
    #- UG
    #- Fondos del Proyecto
    procedencia_fondos = models.CharField(max_length=25, choices=PROCEDENCIA_FONDOS, default='PROY')

    #Nuevos Campos
    objetivo_de_actividad = models.TextField(null=True, blank=True) #Nuevo datos
    descripcion_evaluacion = models.TextField(null=True, blank=True) #Toda la informacion de la planificacion de la actividad
    justificacion_modificacion = models.TextField(null=True, blank=True) #Motivos de modificacion 
    
    #Datos de la actividad segun su tipo
    datos_actividad = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'

    def __str__(self):
        return f'Actividad: {self.codigo}'    