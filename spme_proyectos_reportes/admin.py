import json
from django.contrib import admin
from django.contrib.admin import TabularInline
from django.utils.html import format_html
from .models import (
    BitacoraIndicadorBase, 
    BitacoraIndicadorOG, 
    BitacoraIndicadorOE,
    BitacoraIndicadorROG, 
    BitacoraIndicadorROE
)

# Inline para mostrar bitácoras en otros modelos (opcional)
class BitacoraIndicadorBaseInline(TabularInline):
    model = BitacoraIndicadorBase
    extra = 0
    fields = ('id','tipo_indicador', 'tipo_dato', 'valor_display', 'fecha_registro')
    readonly_fields = ('valor_display',)
    
    def valor_display(self, obj):
        """Muestra el valor según el tipo de dato"""
        if obj.tipo_dato == 'A-Z' and obj.valor_literal:
            return f"Texto: {obj.valor_literal[:50]}..."
        elif obj.tipo_dato == '1-9' and obj.valor_numerico is not None:
            return f"Número: {obj.valor_numerico}"
        elif obj.tipo_dato == '%' and obj.valor_porcentual is not None:
            return f"Porcentaje: {obj.valor_porcentual}%"
        return "Sin valor"
    valor_display.short_description = 'Valor'

# Filtro personalizado para el modelo base
class TipoIndicadorFilter(admin.SimpleListFilter):
    title = 'Tipo de Indicador'
    parameter_name = 'tipo_indicador'
    
    def lookups(self, request, model_admin):
        return BitacoraIndicadorBase.TIPOS_INDICADOR
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tipo_indicador=self.value())
        return queryset

# Admin para el modelo base (abstracto)
@admin.register(BitacoraIndicadorBase)
class BitacoraIndicadorBaseAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'tipo_indicador_display', 
        'tipo_dato_display',
        'valor_formateado',
        'fecha_registro',
        'informe_actividad_link',
        'informe_tarea_link',
        'timestamp_registro'
    )
    
    list_filter = (
        TipoIndicadorFilter,
        'tipo_dato',
        'fecha_registro',
    )
    
    search_fields = (
        'observaciones',
        'valor_literal',
        'id_indicador',
    )
    
    date_hierarchy = 'fecha_registro'
    
    readonly_fields = (
        'tipo_indicador_display',
        'tipo_dato_display',
        'valor_formateado',
        'timestamp_registro',
        'snapshot_display',
    )
    
    fieldsets = (
        ('Información del Indicador', {
            'fields': (
                'tipo_indicador', 
                'tipo_dato', 
                'id_indicador',
                'snapshot_display'
            )
        }),
        ('Valor Registrado', {
            'fields': (
                'valor_formateado',
                'valor_literal',
                'valor_numerico',
                'valor_porcentual',
            )
        }),
        ('Información Adicional', {
            'fields': (
                'fecha_registro',
                'observaciones',
                'archivos_adjuntos',
            )
        }),
        ('Relaciones', {
            'fields': (
                'informe_actividad',
                'informe_tarea',
            ),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('timestamp_registro',),
            'classes': ('collapse',)
        }),
    )
    
    def tipo_indicador_display(self, obj):
        """Muestra el tipo de indicador con formato"""
        tipos_dict = dict(BitacoraIndicadorBase.TIPOS_INDICADOR)
        return tipos_dict.get(obj.tipo_indicador, obj.tipo_indicador)
    tipo_indicador_display.short_description = 'Tipo Indicador'
    
    def tipo_dato_display(self, obj):
        """Muestra el tipo de dato con formato"""
        tipos_dict = dict(BitacoraIndicadorBase.TIPOS_DATO)
        return tipos_dict.get(obj.tipo_dato, obj.tipo_dato)
    tipo_dato_display.short_description = 'Tipo Dato'
    
    def valor_formateado(self, obj):
        """Muestra el valor según el tipo de dato"""
        if obj.tipo_dato == 'A-Z' and obj.valor_literal:
            return format_html('<div style="max-width: 300px; overflow: hidden; text-overflow: ellipsis;">{}</div>', 
                             obj.valor_literal)
        elif obj.tipo_dato == '1-9' and obj.valor_numerico is not None:
            return f"{obj.valor_numerico:,}"
        elif obj.tipo_dato == '%' and obj.valor_porcentual is not None:
            return f"{obj.valor_porcentual}%"
        return "No especificado"
    valor_formateado.short_description = 'Valor'
    
    def informe_actividad_link(self, obj):
        """Enlace al informe de actividad si existe"""
        if obj.informe_actividad:
            url = f"/admin/app_name/infactividad/{obj.informe_actividad.id}/change/"
            return format_html('<a href="{}">Ver Informe #{}</a>', url, obj.informe_actividad.id)
        return "-"
    informe_actividad_link.short_description = 'Informe Actividad'
    
    def informe_tarea_link(self, obj):
        """Enlace al informe de tarea si existe"""
        if obj.informe_tarea:
            url = f"/admin/app_name/inftarea/{obj.informe_tarea.id}/change/"
            return format_html('<a href="{}">Ver Tarea #{}</a>', url, obj.informe_tarea.id)
        return "-"
    informe_tarea_link.short_description = 'Informe Tarea'
    
    def snapshot_display(self, obj):
        """Muestra el snapshot en formato legible"""
        if obj.snapshot_indicador:
            return format_html('<pre style="max-height: 200px; overflow: auto;">{}</pre>', 
                             json.dumps(obj.snapshot_indicador, indent=2, ensure_ascii=False))
        return "Sin snapshot"
    snapshot_display.short_description = 'Snapshot del Indicador'
    
    def get_queryset(self, request):
        """Solo mostrar registros del modelo base (no los hijos)"""
        return super().get_queryset(request).filter(
            polymorphic_ctype__model='bitacoraindicadorbase'
        )
    
    def observaciones_short(self, obj):
        """Muestra observaciones recortadas"""
        if obj.observaciones:
            return obj.observaciones[:100] + "..." if len(obj.observaciones) > 100 else obj.observaciones
        return "-"
    observaciones_short.short_description = 'Observaciones'

# Admin para Indicador OG
@admin.register(BitacoraIndicadorOG)
class BitacoraIndicadorOGAdmin(BitacoraIndicadorBaseAdmin):
    list_display = (
        'id',
        'indicador_og_link',
        'tipo_dato_display',
        'valor_formateado',
        'fecha_registro',
        'observaciones_short',
    )
    
    list_filter = (
        'tipo_dato',
        'fecha_registro',
        'indicador_og',
    )
    
    search_fields = (
        'observaciones',
        'valor_literal',
        'indicador_og__nombre',  # Ajusta según tu modelo real
    )
    
    fieldsets = (
        ('Indicador OG', {
            'fields': ('indicador_og',)
        }),
        ('Valor Registrado', {
            'fields': (
                'tipo_dato',
                'valor_literal',
                'valor_numerico',
                'valor_porcentual',
            )
        }),
        ('Información Adicional', {
            'fields': (
                'fecha_registro',
                'observaciones',
                'archivos_adjuntos',
            )
        }),
        ('Relaciones', {
            'fields': (
                'informe_actividad',
                'informe_tarea',
            ),
            'classes': ('collapse',)
        }),
    )
    
    def indicador_og_link(self, obj):
        """Enlace al indicador OG"""
        if obj.indicador_og:
            url = f"/admin/app_name/indicadorobjetivogeneral/{obj.indicador_og.id}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.indicador_og)
        return "-"
    indicador_og_link.short_description = 'Indicador OG'

# Admin para Indicador OE
@admin.register(BitacoraIndicadorOE)
class BitacoraIndicadorOEAdmin(BitacoraIndicadorBaseAdmin):
    list_display = (
        'id',
        'indicador_oe_link',
        'tipo_dato_display',
        'valor_formateado',
        'fecha_registro',
        'observaciones_short',
    )
    
    list_filter = (
        'tipo_dato',
        'fecha_registro',
        'indicador_oe',
    )
    
    search_fields = (
        'observaciones',
        'valor_literal',
        'indicador_oe__nombre',
    )
    
    fieldsets = (
        ('Indicador OE', {
            'fields': ('indicador_oe',)
        }),
        ('Valor Registrado', {
            'fields': (
                'tipo_dato',
                'valor_literal',
                'valor_numerico',
                'valor_porcentual',
            )
        }),
        ('Información Adicional', {
            'fields': (
                'fecha_registro',
                'observaciones',
                'archivos_adjuntos',
            )
        }),
        ('Relaciones', {
            'fields': (
                'informe_actividad',
                'informe_tarea',
            ),
            'classes': ('collapse',)
        }),
    )
    
    def indicador_oe_link(self, obj):
        """Enlace al indicador OE"""
        if obj.indicador_oe:
            url = f"/admin/app_name/indicadorobjetivoespecifico/{obj.indicador_oe.id}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.indicador_oe)
        return "-"
    indicador_oe_link.short_description = 'Indicador OE'

# Admin para Indicador ROG
@admin.register(BitacoraIndicadorROG)
class BitacoraIndicadorROGAdmin(BitacoraIndicadorBaseAdmin):
    list_display = (
        'id',
        'indicador_rog_link',
        'tipo_dato_display',
        'valor_formateado',
        'fecha_registro',
        'observaciones_short',
    )
    
    list_filter = (
        'tipo_dato',
        'fecha_registro',
        'indicador_rog',
    )
    
    search_fields = (
        'observaciones',
        'valor_literal',
        'indicador_rog__nombre',
    )
    
    fieldsets = (
        ('Indicador ROG', {
            'fields': ('indicador_rog',)
        }),
        ('Valor Registrado', {
            'fields': (
                'tipo_dato',
                'valor_literal',
                'valor_numerico',
                'valor_porcentual',
            )
        }),
        ('Información Adicional', {
            'fields': (
                'fecha_registro',
                'observaciones',
                'archivos_adjuntos',
            )
        }),
        ('Relaciones', {
            'fields': (
                'informe_actividad',
                'informe_tarea',
            ),
            'classes': ('collapse',)
        }),
    )
    
    def indicador_rog_link(self, obj):
        """Enlace al indicador ROG"""
        if obj.indicador_rog:
            url = f"/admin/app_name/indicadorresultadoobjgral/{obj.indicador_rog.id}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.indicador_rog)
        return "-"
    indicador_rog_link.short_description = 'Indicador ROG'

# Admin para Indicador ROE
@admin.register(BitacoraIndicadorROE)
class BitacoraIndicadorROEAdmin(BitacoraIndicadorBaseAdmin):
    list_display = (
        'id',
        'indicador_roe_link',
        'tipo_dato_display',
        'valor_formateado',
        'fecha_registro',
        'observaciones_short',
    )
    
    list_filter = (
        'tipo_dato',
        'fecha_registro',
        'indicador_roe',
    )
    
    search_fields = (
        'observaciones',
        'valor_literal',
        'indicador_roe__nombre',
    )
    
    fieldsets = (
        ('Indicador ROE', {
            'fields': ('indicador_roe',)
        }),
        ('Valor Registrado', {
            'fields': (
                'tipo_dato',
                'valor_literal',
                'valor_numerico',
                'valor_porcentual',
            )
        }),
        ('Información Adicional', {
            'fields': (
                'fecha_registro',
                'observaciones',
                'archivos_adjuntos',
            )
        }),
        ('Relaciones', {
            'fields': (
                'informe_actividad',
                'informe_tarea',
            ),
            'classes': ('collapse',)
        }),
    )
    
    def indicador_roe_link(self, obj):
        """Enlace al indicador ROE"""
        if obj.indicador_roe:
            url = f"/admin/app_name/indicadorresultadoobjespecifico/{obj.indicador_roe.id}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.indicador_roe)
        return "-"
    indicador_roe_link.short_description = 'Indicador ROE'

# Acción personalizada para exportar bitácoras
@admin.action(description="Exportar bitácoras seleccionadas")
def exportar_bitacoras(modeladmin, request, queryset):
    """Acción para exportar bitácoras (implementar según necesidades)"""
    # Aquí puedes implementar la lógica de exportación
    modeladmin.message_user(request, f"{queryset.count()} bitácoras preparadas para exportar")

# Agregar acción a todos los admins
BitacoraIndicadorBaseAdmin.actions = [exportar_bitacoras]
BitacoraIndicadorOGAdmin.actions = [exportar_bitacoras]
BitacoraIndicadorOEAdmin.actions = [exportar_bitacoras]
BitacoraIndicadorROGAdmin.actions = [exportar_bitacoras]
BitacoraIndicadorROEAdmin.actions = [exportar_bitacoras]