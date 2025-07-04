from django.db import models

# Create your models here.
class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.CharField(max_length=50, verbose_name='usuario')
    password = models.TextField(max_length=250,verbose_name='password', blank=False, null=False)
    permisos = models.CharField(max_length=50, verbose_name='permisos', blank=True, null=True)

    def __str__(self):
        return self.usuario

    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
