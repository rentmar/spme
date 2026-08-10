from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from spme_autenticacion.models import Usuario

class Archivo(models.Model):
    """
    Representa un archivo físico almacenado en Garage.
    No sabe nada del contexto de negocio.
    """
    TIPO_ARCHIVO = [
        ('DOCUMENTO', 'Documento'),
        ('IMAGEN', 'Imagen'),
        ('VIDEO', 'Video'),
        ('AUDIO', 'Audio'),
        ('OTRO', 'Otro'),
    ]

    #Nombre original de archivo
    nombre_original = models.CharField(
        max_length=500,
        help_text="Nombre original del archivo al ser subido"
    )
    #Nombre en el repositorio
    nombre_storage = models.CharField(
        max_length=255,
        help_text="Nombre sanitizado usado en Garage"
    )
    #tipo de archivo
    tipo_archivo = models.CharField(
        max_length=20,
        choices=TIPO_ARCHIVO,
        default='OTRO',
        help_text="Tipo de archivo determinado por el backend"
    )
    mime_type = models.CharField(max_length=100)
    #Tamaño en bytes
    tamano = models.BigIntegerField(help_text="Tamaño en bytes")
    #bucket en el repositorio
    bucket = models.CharField(max_length=100)
    #key en el repositorio
    key = models.CharField(
        max_length=255,
        unique=True,
        help_text="Ruta completa del archivo en Garage. Única globalmente."
    )
    #hash unico para los archivos
    hash_sha256 = models.CharField(
        max_length=64,
        help_text="SHA256 para verificar integridad y detectar duplicados"
    )
    # Auditoría
    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='archivos_creados'
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Archivo'
        verbose_name_plural = 'Archivos'
        indexes = [
            models.Index(fields=['hash_sha256']),
        ]
        ordering = ['-creado_en']

    def __str__(self):
        return self.nombre_original


class Adjunto(models.Model):
    """
    Asocia un Archivo con cualquier objeto de negocio mediante ContentType.

    Un mismo archivo puede estar asociado a múltiples objetos,
    y un objeto puede tener múltiples archivos.

    Sin limit_choices_to: cualquier modelo puede tener adjuntos.
    La capa de aplicación decide qué modelos están habilitados.
    """
    #Relacion FK a los archivos
    archivo = models.ForeignKey(
        Archivo,
        on_delete=models.CASCADE,
        related_name='adjuntos'
    )
    #Relacion Generica a los nodos
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField() #Identificador del nodo
    content_object = GenericForeignKey('content_type', 'object_id') #contenido

    #Metadatos del adjunto
    descripcion = models.TextField(blank=True)
    orden = models.PositiveIntegerField(default=0)

    #Auditoria
    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='adjuntos_creados'
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Adjunto'
        verbose_name_plural = 'Adjuntos'
        ordering = ['orden', '-creado_en']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"{self.archivo.nombre_original} → {self.content_type.model}#{self.object_id}"





