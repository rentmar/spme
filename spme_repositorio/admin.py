from django.contrib import admin
from spme_repositorio.models import Archivo, Adjunto


@admin.register(Archivo)
class ArchivoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre_original', 'tipo_archivo', 'mime_type', 'tamano', 'creado_por', 'creado_en']
    list_filter = ['tipo_archivo', 'mime_type', 'creado_en']
    search_fields = ['nombre_original', 'key', 'hash_sha256']
    readonly_fields = ['creado_en']


@admin.register(Adjunto)
class AdjuntoAdmin(admin.ModelAdmin):
    list_display = ['id', 'archivo', 'content_type', 'object_id', 'descripcion', 'orden', 'creado_por', 'creado_en']
    list_filter = ['content_type', 'creado_en']
    search_fields = ['descripcion']
    readonly_fields = ['creado_en']