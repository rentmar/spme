from django.db import models

class EstructuraPei(models.Model):
    id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=50, verbose_name='tiulo')
    descripcion = models.TextField(max_length=250,verbose_name='descripcion', blank=False, null=False)
    fecha_creacion = models.DateTimeField(verbose_name='fecha_creacion')
    fecha_inicio = models.DateField(verbose_name='fecha_inicio')
    fecha_fin = models.DateField(verbose_name='fecha_fin')
    esta_vigente = models.BooleanField(verbose_name='esta_vigente')
    creado_el = models.DateTimeField(verbose_name='creado_el')
    modificado_el = models.DateTimeField(verbose_name='modificado_el')

    def __str__(self):
        return self.titulo

    class Meta:
        db_table = 'spme_estructuracion_pei'
        verbose_name = 'Estructuracion_pei'
        verbose_name_plural = 'No definidos'
