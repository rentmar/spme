from django.db import models
from .departamentos import DepartamentoBolivia

#Modelo de la Institución
class Institucion(models.Model):
    sigla = models.CharField(max_length=50, blank=True, null=True)
    nombre = models.CharField(max_length=500, blank=True, null=True)
    #Contacto institucional
    emailInstitucion = models.CharField(max_length=150, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    #Ubicacion de la sede principal
    direccion = models.TextField(blank=True, null=True)
    ciudad = models.CharField(max_length=50, blank=True, null=True)
    departamentoSede = models.ForeignKey(
        DepartamentoBolivia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='instituciones_sede',
        verbose_name='Departamento de la sede principal',
    )
    casillaPostal = models.CharField(max_length=150, blank=True, null=True)
    webSite = models.CharField(max_length=300, blank=True, null=True)

    #Departamentos donde desarrolla intervencion
    departamentoIntervencion = models.ManyToManyField(
        DepartamentoBolivia, 
        related_name='instituciones', 
        verbose_name='Departamentos de intervencion',
        blank=True,
    )
    
    class Meta:
        verbose_name = "Institucion"
        verbose_name_plural = "Instituciones"
        ordering = ['sigla']
    
    def __str__(self):
        return self.sigla or self.nombre or f"Institución {self.id}"
    
    @property
    def total_proyectos(self):
        """Cantidad de proyectos de esta institución"""
        return self.proyectos.count()
    
    @property
    def proyectos_activos(self):
        """Proyectos activos de esta institución"""
        return self.proyectos.filter(estado='PL')  

