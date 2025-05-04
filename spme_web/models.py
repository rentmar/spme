from django.db import models

# Create your models here.

class Tarea(models.Model):
    nombre = models.TextField(blank=True, null=True)
    numero = models.IntegerField(blank=True, null=True)


