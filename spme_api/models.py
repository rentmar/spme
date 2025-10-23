from django.db import models

# Create your models here.
class Libro(models.Model):
    codigo = models.IntegerField(null=True, blank=True)
    titulo = models.CharField(null=True, blank=True, max_length=255)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo
