from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from spme_repositorio.models import Archivo, Adjunto, ReferenciaExterna
from auditlog.models import LogEntry
from auditlog.admin import LogEntryAdmin


@admin.register(Archivo)
class ArchivoAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'nombre_original',
        'tipo_archivo',
        'mime_type',
        'tamano_legible',
        'creado_por',
        'creado_en',
    ]
    list_filter = ['tipo_archivo', 'mime_type', 'creado_en']
    search_fields = ['nombre_original', 'key', 'hash_sha256']
    readonly_fields = ['creado_en']
    ordering = ['-creado_en']   # ⭐ Últimos primero
    list_per_page = 50

    @admin.display(description='Tamaño')
    def tamano_legible(self, obj):
        """Convierte bytes a KB/MB legible."""
        if not obj.tamano:
            return '—'
        size = obj.tamano
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f'{size:.1f} {unit}'
            size /= 1024
        return f'{size:.1f} TB'


@admin.register(Adjunto)
class AdjuntoAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'nombre_archivo',
        'content_type',
        'object_id',
        'descripcion_corta',
        'orden',
        'creado_por',
        'creado_en',
    ]
    list_filter = ['content_type', 'creado_en']
    search_fields = [
        'descripcion',
        'archivo__nombre_original',
        'object_id',
        'archivo__hash_sha256',
    ]
    readonly_fields = ['creado_en']
    ordering = ['-id']           # ⭐ Últimos primero (por id descendente)
    list_per_page = 50
    date_hierarchy = 'creado_en'  # ⭐ Navegación por fecha
    list_select_related = ['archivo', 'content_type', 'creado_por']  # ⭐ Optimiza queries

    @admin.display(description='Archivo', ordering='archivo__nombre_original')
    def nombre_archivo(self, obj):
        """Muestra el nombre del archivo asociado."""
        return obj.archivo.nombre_original

    @admin.display(description='Descripción')
    def descripcion_corta(self, obj):
        """Trunca la descripción si es muy larga."""
        if not obj.descripcion:
            return '—'
        return obj.descripcion[:60] + ('…' if len(obj.descripcion) > 60 else '')


@admin.register(ReferenciaExterna)
class ReferenciaExternaAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'nombre',
        'categoria',
        'url_corta',
        'content_type',
        'object_id',
        'orden',
        'creado_por',
        'creado_en',
    ]
    list_filter = ['categoria', 'content_type', 'creado_en']
    search_fields = ['nombre', 'url', 'descripcion']
    readonly_fields = ['creado_en']
    ordering = ['-id']           # ⭐ Últimos primero
    list_per_page = 50
    date_hierarchy = 'creado_en'

    @admin.display(description='URL')
    def url_corta(self, obj):
        """Trunca la URL si es muy larga."""
        if not obj.url:
            return '—'
        return obj.url[:50] + ('…' if len(obj.url) > 50 else '')