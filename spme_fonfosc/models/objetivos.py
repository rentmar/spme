from django.db import models

#Objetivo del Proyecto
class ObjetivoFonfosc(models.Model):
    codigo = models.CharField(max_length=50)
    redaccion = models.TextField(blank=True, null=True)
    supuestosRiesgos = models.TextField(blank=True, null=True)
