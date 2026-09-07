from django.db import models
from polymorphic.models import PolymorphicModel

class IndicadorBaseFonFosc(PolymorphicModel):

    nombre = models.CharField(
        max_length=255
    )

    descripcion = models.TextField(
        blank=True,
        null=True
    )