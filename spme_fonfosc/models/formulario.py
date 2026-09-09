from django.db import models
from spme_autenticacion.models import Usuario


class Formulario(models.Model):
    """
    Modelo para el almacenamiento de formularios
    """
    ESTADOS = [
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
        ('archived', 'Archivado'),
    ]
    #Datos generales
    nombre = models.CharField(max_length=200)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    version = models.IntegerField(default=1)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='draft')

    #Estructura del formulario
    definicion_json = models.JSONField()

    #Audit
    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='formularios_creados',   
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_actualizacion']