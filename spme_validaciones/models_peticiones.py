# spme_validaciones/models_peticiones.py

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from spme_autenticacion.models import Usuario
from .constants_peticiones import ESTADOS_PETICION, ESTADO_INICIADA


class TipoPeticionModificacion(models.Model):
    """
    Catálogo de tipos de petición de modificación.
    Extensible sin migración: se agrega una fila y un handler en código.
    """
    codigo = models.SlugField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    esquema_payload = models.JSONField(blank=True, null=True)
    content_types_permitidos = models.JSONField(
        default=list,
        help_text='Lista de "app_label.model" permitidos como objetivo'
    )
    requiere_versionado = models.BooleanField(default=False)
    orden = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Tipo de petición de modificación'
        verbose_name_plural = 'Tipos de peticiones de modificación'
        ordering = ['orden', 'codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class PeticionModificacion(models.Model):
    """
    Petición de modificación sobre un documento cerrado.
    Una sola INICIADA por objetivo (partial unique index).
    """
    tipo = models.ForeignKey(
        TipoPeticionModificacion,
        on_delete=models.PROTECT,
        related_name='peticiones',
    )

    # Objetivo vía ContentType
    objetivo_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        related_name='peticiones_modificacion',
    )
    objetivo_object_id = models.BigIntegerField()
    objetivo = GenericForeignKey('objetivo_content_type', 'objetivo_object_id')

    solicitante = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='peticiones_modificacion_iniciadas',
    )
    justificativo = models.TextField()
    payload = models.JSONField(default=dict)

    estado = models.CharField(
        max_length=30,
        choices=ESTADOS_PETICION,
        default=ESTADO_INICIADA,
    )

    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    motivo_anulacion = models.TextField(null=True, blank=True)

    resuelto_por = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='peticiones_modificacion_resueltas',
        null=True,
        blank=True,
    )

    # Para EDICION_TOTAL: cuándo el frontend consumió la autorización
    fecha_consumo = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Petición de modificación'
        verbose_name_plural = 'Peticiones de modificación'
        ordering = ['-fecha_inicio']
        indexes = [
            models.Index(fields=['objetivo_content_type', 'objetivo_object_id']),
            models.Index(fields=['estado']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['objetivo_content_type', 'objetivo_object_id'],
                condition=models.Q(estado=ESTADO_INICIADA),
                name='unique_peticion_iniciada_por_objetivo',
            ),
        ]

    def __str__(self):
        return f"Petición #{self.pk} {self.tipo.codigo} sobre {self.objetivo_content_type}#{self.objetivo_object_id} [{self.estado}]"


class DocumentoVersion(models.Model):
    """
    Snapshot del contenido de un documento al momento de ejecutarse una
    petición de tipo EDICION_TOTAL (u otra que requiera versionado).
    """
    documento_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        related_name='versiones_documento',
    )
    documento_object_id = models.BigIntegerField()
    documento = GenericForeignKey('documento_content_type', 'documento_object_id')

    numero_version = models.IntegerField()
    contenido_snapshot = models.JSONField()

    peticion_origen = models.ForeignKey(
        PeticionModificacion,
        on_delete=models.PROTECT,
        related_name='versiones_generadas',
        null=True,
        blank=True,
    )
    aprobado_por = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='versiones_aprobadas',
    )
    fecha_snapshot = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Versión de documento'
        verbose_name_plural = 'Versiones de documento'
        ordering = ['-fecha_snapshot']
        constraints = [
            models.UniqueConstraint(
                fields=['documento_content_type', 'documento_object_id', 'numero_version'],
                name='unique_version_por_documento',
            ),
        ]
        indexes = [
            models.Index(fields=['documento_content_type', 'documento_object_id']),
        ]

    def __str__(self):
        return f"v{self.numero_version} de {self.documento_content_type}#{self.documento_object_id}"