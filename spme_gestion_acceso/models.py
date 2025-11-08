from django.db import models
from spme_autenticacion.models import Usuario
from spme_estructuracion_proyecto.models import InstanciaGestora, Proyecto

#Permisos de Instancia Gestora
class UserInstanciaGestora(models.Model):
    LECTURA = 1
    EDICION = 2
    ADMINISTRACION = 3

    NIVEL_ACCESO_CHOICES = [
        (LECTURA, 'Solo lectura'),
        (EDICION, 'Edicion'),
        (ADMINISTRACION, 'Administracion')
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='instancias_gestoras_usuario',
    )

    instancia_gestora = models.ForeignKey(
        InstanciaGestora,
        on_delete=models.CASCADE,
        related_name='usuarios_instancia',
    )

    nivel_acceso = models.IntegerField(choices=NIVEL_ACCESO_CHOICES, default=LECTURA)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = ['usuario', 'instancia_gestora']
        verbose_name = 'Usuario - Instancia Gestora'
        verbose_name_plural = 'Usuarios - Instancias Gestoras'

    def __str__(self):
        nivel_texto = dict(self.NIVEL_ACCESO_CHOICES).get(self.nivel_acceso, 'Desconocido')
        return f"{self.usuario.username} - {self.instancia_gestora.instancia} ({nivel_texto})"


#Permisos para los proyectos
class PermisoProyectoEspecifico(models.Model):
    LECTURA = 1
    EDICION = 2
    ADMINISTRACION = 3

    TIPO_ACCESO_CHOICES = [
        (LECTURA, 'Solo lectura'),
        (EDICION, 'Edicion'),
        (ADMINISTRACION, 'Administracion'),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='permisos_proyectos_especificos',
    )

    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='permisos_usuarios_especificos'
    )

    tipo_acceso = models.IntegerField(choices=TIPO_ACCESO_CHOICES, default=LECTURA)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)

    asignado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='permisos_otorgados'
    )

    motivo = models.TextField(blank=True, help_text='Justificacion del permiso')
    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = ['usuario', 'proyecto']
        verbose_name = 'Permiso Específico de Proyecto'
        verbose_name_plural = 'Permisos Específicos de Proyectos'

    def __str__(self):
        tipo_texto = dict(self.TIPO_ACCESO_CHOICES).get(self.tipo_acceso, 'Desconocido')
        return f"{self.usuario.username} - {self.proyecto.codigo} ({tipo_texto})"    




