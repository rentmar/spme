from django.db import models


#Modelo Departamento Bolivia

class DepartamentoBolivia(models.Model):
    codigo = models.CharField(max_length=5)
    nombre = models.CharField(max_length=100)
    class Meta:
        verbose_name = "Departamento Bolivia"
        verbose_name_plural = "Departamentos Bolivia"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre