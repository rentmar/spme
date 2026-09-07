from django.db import models


class ResultadoFonfosc(models.Model):
    codigo = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    descripcion = models.TextField(
        blank=True
    )

    supuestosRiesgos = models.TextField(
        blank=True
    )