from django.db import models
from spme_estructuracion_proyecto.models import Proyecto
from django.db import models

 
#Almacena la planificacion completa de un proyecto para seguimiento
class PlanificacionProyecto(models.Model):
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='planificaciones',
        blank=True,
        null=True,
    )
    table_config = models.JSONField(null=True, blank=True)
    rows_data = models.JSONField(null=True, blank=True)
    version = models.IntegerField(default=1)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    creado_por = models.CharField(max_length=255, null=True, blank=True)
    vigente = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-version']
        unique_together = ['proyecto', 'version']
        verbose_name = 'Planificacion Proyecto'
        verbose_name_plural = 'Planificaciones Proyecto'

    def __str__(self):
        return f'Plan de {self.proyecto} - version {self.version}'    



#Registra cambios especificos en la planificacion
class CambioPlanificacion(models.Model):
    TIPO_CAMBIO = [
        ('creacion', 'Creación'),
        ('actualizacion', 'Actualización'),
        ('eliminacion', 'Eliminación'),
        ('reprogramacion', 'Reprogramación'),
    ]    
    planificacion = models.ForeignKey(
        PlanificacionProyecto,
        on_delete=models.CASCADE,
        related_name='cambios',
        blank=True,
        null=True,
    )
    tipo_cambio = models.CharField(max_length=20, choices=TIPO_CAMBIO)
    datos_anteriores = models.JSONField(null=True, blank=True)
    datos_nuevos = models.JSONField(null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    realizado_por = models.CharField(max_length=255, null=True, blank=True)
    realizado_el = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-realizado_el']
        verbose_name = 'Cambio planificacion'
        verbose_name_plural = 'Cambios planificacion'

    def __str__(self):
        return f'Cambio para: { self.planificacion }'    





#Proyecto de planificaciones
class ProyectoPlan(models.Model):
    table_config = models.JSONField(null=True, blank=True)
    rows_data = models.JSONField(null=True, blank=True)
    version = models.IntegerField(default=1)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    #Relacion
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='planificacion'
    )

#Revision de plan
class PlanRevision(models.Model):
    cambios = models.JSONField(null=True, blank=True)
    razon = models.TextField(null=True, blank=True)
    #modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    modificado_por = models.CharField(null=True, blank=True, max_length=100)
    modificado_el = models.DateTimeField(auto_now_add=True)
    version = models.IntegerField()
    #Relacion
    plan = models.ForeignKey(
        ProyectoPlan,
        on_delete=models.CASCADE,
        related_name='revisiones'
    )
    class Meta:
        ordering = ['-modificado_el']

