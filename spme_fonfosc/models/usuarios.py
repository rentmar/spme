from django.db import models
from django.conf import settings

from spme_autenticacion.models import Usuario
from .instituciones import Institucion

class UsuarioFonFosc(models.Model):
    """
    Extension para los usuacios FonFosc
    """
    #usuario
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='perfil_fonfosc',
    )

    #institucion
    institucion = models.ForeignKey(
        Institucion,
        on_delete=models.CASCADE,
        related_name='usuarios_fonfosc'
    )

    telefono = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )

    #Fecha de registro
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Usuario FONFOSC"
        verbose_name_plural = "Usuarios FONFOSC"
        ordering = ['usuario__username']

    def __str__(self):
        return f"{self.usuario.username} - {self.institucion.sigla or self.institucion.nombre}"