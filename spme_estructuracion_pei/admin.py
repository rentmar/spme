from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Pei, 
    ObjetivoPei, 
    FactoresCriticos, 
    IndicadorPeiCualitativo, 
    IndicadorPeiCuantitativo, 
    ActividadPei, 
    TareaActividadPei, 
    IndicadorPeiBase)

# Register your models here.

#admin.site.register(Pei)
#admin.site.register(ObjetivoPei)
admin.site.register(FactoresCriticos)
#admin.site.register(IndicadorPeiCuantitativo)
#admin.site.register(IndicadorPeiCualitativo)
#admin.site.register(ActividadPei)
#admin.site.register(TareaActividadPei)
#admin.site.register(IndicadorPeiBase)

#Vista para los PEIs
@admin.register(Pei)
class PeiAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'esta_vigente', 'fecha_inicio', 'fecha_fin', 'creado_el')
    list_filter = ('esta_vigente', 'fecha_inicio', 'fecha_fin')
    search_fields = ('titulo', 'descripcion')
    ordering = ('-creado_el',)


@admin.register(ActividadPei)
class ActividadPeiAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombreCorto', 'estado', 'fecha_inicio', 'responsable')
    list_filter = ('estado', 'pei')
    search_fields = ('codigo', 'nombreCorto')
    list_editable = ('estado',)

@admin.register(TareaActividadPei)
class TareaActividadPeiAdmin(admin.ModelAdmin):
    # Lista principal
    list_display = ('codigo', 'titulo', 'actividad', 'estado', 'fecha_limite', 'presupuesto')
    
    # Filtros
    list_filter = ('estado', 'actividad', 'fecha_limite')
    
    # Búsqueda
    search_fields = ('codigo', 'titulo', 'actividad__codigo')
    
    # Campos editables
    list_editable = ('estado',)
    
    # Acciones básicas
    actions = ['marcar_como_completadas']
    
    def marcar_como_completadas(self, request, queryset):
        from django.utils import timezone
        queryset.update(estado='COMPL', fecha_ejecucion=timezone.now().date())
        self.message_user(request, f'{queryset.count()} tarea(s) completada(s).')
    marcar_como_completadas.short_description = "Marcar como Completadas"



@admin.register(ObjetivoPei)
class ObjetivoPeiAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'codigo',
        'descripcion_short',
        'pei_link',
        'total_indicadores',
        'creado_el',
        'modificado_el'
    ]
    
    list_filter = [
        'creado_el',
        'modificado_el'
    ]
    
    search_fields = [
        'codigo',
        'descripcion',
        'pei__nombre'
    ]
    
    ordering = ['codigo']
    
    readonly_fields = ['creado_el', 'modificado_el']
    
    # Métodos personalizados
    def descripcion_short(self, obj):
        """Muestra solo los primeros 50 caracteres de la descripción"""
        if obj.descripcion:
            return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
        return '-'
    descripcion_short.short_description = 'Descripción'
    
    def pei_link(self, obj):
        """Muestra el PEI relacionado con enlace"""
        if obj.pei:
            return format_html(
                '<a href="{}">{}</a>',
                f'/admin/spme_estructuracion_pei/pei/{obj.pei.id}/change/',
                str(obj.pei)
            )
        return '-'
    pei_link.short_description = 'PEI'
    
    def total_indicadores(self, obj):
        """Cuenta cuántos indicadores tiene este objetivo"""
        count = obj.indicador_pei_objetivo.count()
        return format_html(
            '<a href="{}?objetivo__id__exact={}">{}</a>',
            '/admin/spme_estructuracion_pei/indicadorpeibase/',
            obj.id,
            count
        )
    total_indicadores.short_description = 'Indicadores'
    
    # Configuración de campos en la vista de edición
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'descripcion', 'pei')
        }),
        ('Metadatos', {
            'fields': ('creado_el', 'modificado_el'),
            'classes': ('collapse',)
        }),
    )

@admin.register(IndicadorPeiBase)
class IndicadorPeiBaseAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'codigo',
        'descripcion_short',
        'objetivo_link',
        'tipo_indicador',
        'responsabilidad',
        'frecuencia_recopilacion',
        'creado_el'
    ]
    
    list_filter = [
        'responsabilidad',
        'frecuencia_recopilacion',
        'creado_el',
        'modificado_el'
    ]
    
    search_fields = [
        'codigo',
        'descripcion',
        'captura_informacion',
        'responsabilidad',
        'objetivo__codigo',
        'objetivo__descripcion'
    ]
    
    list_select_related = ['objetivo']
    
    ordering = ['codigo']
    
    readonly_fields = ['creado_el', 'modificado_el']
    
    autocomplete_fields = ['objetivo']
    
    # Métodos personalizados
    def descripcion_short(self, obj):
        """Muestra descripción corta"""
        if obj.descripcion:
            return obj.descripcion[:60] + '...' if len(obj.descripcion) > 60 else obj.descripcion
        return '-'
    descripcion_short.short_description = 'Indicador'
    
    def objetivo_link(self, obj):
        """Muestra el objetivo con enlace"""
        if obj.objetivo:
            return format_html(
                '<a href="{}">{}</a>',
                f'/admin/spme_estructuracion_pei/objetivopei/{obj.objetivo.id}/change/',
                obj.objetivo.codigo
            )
        return '-'
    objetivo_link.short_description = 'Objetivo'
    
    def tipo_indicador(self, obj):
        """Determina el tipo de indicador"""
        if hasattr(obj, 'indicadorpeicuantitativo'):
            return 'CUANTITATIVO'
        elif hasattr(obj, 'indicadorpeicualitativo'):
            return 'CUALITATIVO'
        return 'BASE'
    tipo_indicador.short_description = 'Tipo'
    
    # Configuración de campos en la vista de edición
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'descripcion', 'objetivo')
        }),
        ('Información Adicional', {
            'fields': ('captura_informacion', 'responsabilidad', 'frecuencia_recopilacion', 'uso_informacion')
        }),
        ('Metadatos', {
            'fields': ('creado_el', 'modificado_el'),
            'classes': ('collapse',)
        }),
    )

# Admin para los tipos específicos de indicadores
@admin.register(IndicadorPeiCuantitativo)
class IndicadorPeiCuantitativoAdmin(IndicadorPeiBaseAdmin):
    # Hereda de IndicadorPeiBaseAdmin y añade campos específicos
    list_display = IndicadorPeiBaseAdmin.list_display.copy()
    list_display.extend(['numerador_short', 'denominador_short'])
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'descripcion', 'objetivo')
        }),
        ('Información Adicional', {
            'fields': ('captura_informacion', 'responsabilidad', 'frecuencia_recopilacion', 'uso_informacion')
        }),
        ('Datos Cuantitativos', {
            'fields': (
                'numerador', 
                'denominador', 
                'umbral_des_numeral',
                'umbral_des_literal_um1',
                'umbral_des_literal_um2',
                'umbral_des_literal_um3'
            )
        }),
        ('Metadatos', {
            'fields': ('creado_el', 'modificado_el'),
            'classes': ('collapse',)
        }),
    )
    
    def numerador_short(self, obj):
        if obj.numerador:
            return obj.numerador[:30] + '...' if len(obj.numerador) > 30 else obj.numerador
        return '-'
    numerador_short.short_description = 'Numerador'
    
    def denominador_short(self, obj):
        if obj.denominador:
            return obj.denominador[:30] + '...' if len(obj.denominador) > 30 else obj.denominador
        return '-'
    denominador_short.short_description = 'Denominador'

@admin.register(IndicadorPeiCualitativo)
class IndicadorPeiCualitativoAdmin(IndicadorPeiBaseAdmin):
    # Hereda de IndicadorPeiBaseAdmin
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'descripcion', 'objetivo')
        }),
        ('Información Adicional', {
            'fields': ('captura_informacion', 'responsabilidad', 'frecuencia_recopilacion', 'uso_informacion')
        }),
        ('Umbrales Cualitativos', {
            'fields': (
                'umbral_des_literal_um1',
                'umbral_des_literal_um2',
                'umbral_des_literal_um3'
            )
        }),
        ('Metadatos', {
            'fields': ('creado_el', 'modificado_el'),
            'classes': ('collapse',)
        }),
    )
