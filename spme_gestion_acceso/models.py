#spme_gestion_acceso/models.py
from django.db import models
from spme_autenticacion.models import Usuario
from spme_estructuracion_proyecto.models import InstanciaGestora, Proyecto
from .constants import NivelesAcceso
from django.utils.timezone import now



# ======================================
# Usuario ↔ Instancia Gestora
# ======================================
class UserInstanciaGestora(models.Model):
    """
    Relacion Usuario <-> Instancia Gestora (IG)
    Define el nivel de acceso del usuario dentro de la IG.
    Permisos de IG se aplican a todos los proyectos de la misma.
    """
   
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

    #Nivel de acceso - control de datos a nivel IG 
    nivel_acceso = models.IntegerField(
        choices=NivelesAcceso.CHOICES, 
        default=NivelesAcceso.LECTURA,
    )

    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = ['usuario', 'instancia_gestora']
        verbose_name = 'Usuario - Instancia Gestora'
        verbose_name_plural = 'Usuarios - Instancias Gestoras'

    def __str__(self):
        #nivel_texto = dict(NivelesAcceso.CHOICES).get(self.nivel_acceso, 'Desconocido')
        #return f"{self.usuario.username} - {self.instancia_gestora.instancia} ({nivel_texto})"
        #nivel_texto = dict(self.NIVEL_ACCESO_CHOICES).get(self.nivel_acceso, 'Desconocido')
        #return f"{self.usuario.username} - {self.instancia_gestora.instancia} ({nivel_texto})"
        return f'{self.usuario.username} - {self.instancia_gestora} ({NivelesAcceso.NOMBRES.get(self.nivel_acceso)})'


# ======================================
# Permiso explicito del Proyecto
# ======================================
class PermisoProyectoEspecifico(models.Model):
    """
    Permiso explicito de un usuario sobre un proyecto
    Prevalece sobre permisos heredados sobre IG
    """
    
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

    #Se utiliza NivelesAccesos, semantica = control de datos
    tipo_acceso = models.IntegerField(
        choices=NivelesAcceso.CHOICES, 
        default=NivelesAcceso.LECTURA
    )
    
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
        # tipo_texto = dict(self.TIPO_ACCESO_CHOICES).get(self.tipo_acceso, 'Desconocido')
        # return f"{self.usuario.username} - {self.proyecto.codigo} ({tipo_texto})"  
        return f'{self.usuario.username} - {self.proyecto.codigo} ({NivelesAcceso.NOMBRES.get(self.tipo_acceso)})'

    @property
    def vigente(self):
        """
        Determina si el permiso esta vigente
        - activo
        - fecha de expiracion        
        """
        if not self.activo:
            return False
        
        if self.fecha_expiracion:
            return self.fecha_expiracion > now()
        return True


      




