from django.db import models
from spme_estructuracion_proyecto.models import Proyecto
from django.db import models


#Almacena la planificacion completa de un proyecto
class PlanificacionProyecto(models.Model):
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='planificaciones',
        blank=True,
        null=True,
    )
    table_config = models.JSONField(null=True, blank=True)
    rows_data = models.JSONField()
    version = models.IntegerField(default=1)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    creado_por = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        ordering = ['-version']
        unique_together = ['proyecto', 'version']


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
    modificado_por = models.CharField(null=True, blank=True)
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

