from django.db import models
from spme_estructuracion_pei.models import Pei
from .instituciones import Institucion

class ProyectoFonFosc(models.Model):
    ESTADO_OPCIONES = [
        ('ES', 'Estructuración'),
        ('PL', 'Planificado'),
        ('OBS', 'Observado'),
        ('APROB', 'Aprobado'),
        ('EJ', 'En Ejecución'),
        ('FIN', 'Finalizado'),
    ]

    CATEGORIA_PROYECTO = [
        ('FI', 'Fortalecimiento Institucional'),
        ('FSC', 'Fortalecimiento de la Sociedad Civil'),
    ]

    # Información básica
    codigo = models.CharField(
        max_length=50,
        unique=True
    )

    titulo = models.TextField(
        null=True,
        blank=True
    )

    descripcion = models.TextField(
        blank=True,
        null=True
    )
    # Clasificación
    categoria = models.CharField(
        max_length=3,
        choices=CATEGORIA_PROYECTO,
        default='FI'
    )

    cobertura_geografica = models.TextField(
        blank=True,
        null=True
    )

    # Estado
    estado = models.CharField(
        max_length=10,
        choices=ESTADO_OPCIONES,
        default='ES'
    )

    # Institución responsable
    institucion = models.ForeignKey(
        Institucion,
        on_delete=models.PROTECT,
        related_name='proyectos',
        verbose_name='Institución responsable',
        help_text='Institución a la que pertenece este proyecto'
    )

    # PEI asociado
    pei = models.ForeignKey(
        Pei,
        on_delete=models.PROTECT,
        related_name='proyectos_fonfosc',
        verbose_name='PEI asociado'
    )

    class Meta:
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'

        indexes = [
            models.Index(
                fields=['institucion', 'estado']
            ),
            models.Index(
                fields=['codigo']
            ),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.titulo}"

    @property
    def institucion_info(self):
        if self.institucion:
            return self.institucion.sigla or self.institucion.nombre

        return "Sin institución asignada"



