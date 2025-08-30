from django.db import models

#Programa/Area puede contener varios proyectos
class Programa(models.Model):
    """
    Representa un Programa que puede contener varios Proyectos.
    """
    TIPO_PROGRAMA = [
        ('PROGRAMA', 'Programa'),
        ('AREA', 'Area'),
    ]
    codigo = models.CharField(max_length=20, blank=True, null=True)
    nombre = models.CharField(max_length=400)
    descripcion = models.TextField(blank=True, null=True)
    tipo =  models.CharField(max_length=20, choices=TIPO_PROGRAMA, default='PROGRAMA')

    def __str__(self):
        return self.nombre
