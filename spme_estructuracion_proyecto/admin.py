from django.contrib import admin
from .models import *
from django.utils.html import format_html


# Register your models here.
admin.site.register(InstanciaGestora)
admin.site.register(ProcedenciaFondos)
admin.site.register(DiagramaEstructura)
#admin.site.register(Proyecto)
admin.site.register(IndicadorProyecto)
admin.site.register(IndicadorObjetivoGeneral)
admin.site.register(IndicadorObjetivoEspecifico)
admin.site.register(IndicadorResultadoObjGral)
admin.site.register(IndicadorResultadoObjEspecifico)
#admin.site.register(ObjetivoGeneralProyecto)
admin.site.register(Proceso)


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    """
    Admin para el modelo Proyecto.
    Muestra información relevante incluyendo:
    - Código y título
    - Creado por (campo legado)
    - Propietario (usuario dueño para permisos)
    - Instancia(s) gestora(s)
    - Estado y fechas
    """

    # Campos que se mostrarán en la lista
    list_display = (
        'id',
        'codigo',
        'titulo',
        'creado_por',    # mostrar nombre en lugar de CharField plano
        'propietario',       # FK a Usuario
        'get_instancias',    # mostrar todas las IGs relacionadas
        'estado',
        'fecha_inicio',
        'fecha_finalizacion',
    )

    # Filtros laterales
    list_filter = ('estado', 'instancia_gestora', 'propietario')

    # Búsqueda por campos clave
    search_fields = ('codigo', 'titulo', 'creado_por', 'propietario__username')

    # Campos que se pueden editar directamente desde la lista
    list_editable = ('estado', 'propietario',)

    # Orden por defecto
    ordering = ('-fecha_creacion',)

    # Campos de solo lectura
    readonly_fields = ('fecha_creacion',)

    # Muestra de campos ManyToMany
    filter_horizontal = ('instancia_gestora', 'procedencia_fondos')

    def get_instancias(self, obj):
        """
        Muestra las Instancias Gestoras asociadas como lista
        """
        return ", ".join([ig.__str__() for ig in obj.instancia_gestora.all()])
    get_instancias.short_description = "Instancia(s) Gestora(s)"


@admin.register(ObjetivoGeneralProyecto)
class ObjetivoGeneralProyectoAdmin(admin.ModelAdmin):
    """Admin para Objetivo General del Proyecto"""
    
    # Campos a mostrar en la lista
    list_display = [
        'id',
        'codigo_display',
        'proyecto_display',
        'proyecto_id_display',  # Nueva columna para ID del proyecto
        'descripcion_truncada',
        'has_supuestos',
        'has_riesgos',
    ]
    
    # Campos para buscar
    search_fields = [
        'codigo',
        'descripcion',
        'proyecto__codigo',
        'proyecto__nombre',
        'proyecto__id',  # Permite buscar por ID del proyecto
    ]
    
    # Filtros en la barra lateral
    list_filter = [
        'proyecto__estado',
    ]
    
    # Campos de solo lectura (si es necesario)
    readonly_fields = ['codigo', 'proyecto']
    
    # Organización de campos en el formulario de edición
    fieldsets = (
        ('Información Básica', {
            'fields': ('proyecto', 'codigo')
        }),
        ('Descripción del Objetivo', {
            'fields': ('descripcion',)
        }),
        ('Consideraciones', {
            'fields': ('supuestos', 'riesgos'),
            'classes': ('collapse',),  # Opcional: colapsar esta sección
        }),
    )
    
    # Campos para ordenar
    ordering = ['proyecto__codigo', 'codigo']
    
    # Campos de autocompletar (si es necesario)
    autocomplete_fields = ['proyecto']
    
    def codigo_display(self, obj):
        """Muestra el código con formato"""
        return f"OO-{obj.codigo}" if obj.codigo else "Sin código"
    codigo_display.short_description = 'Código'
    codigo_display.admin_order_field = 'codigo'
    
    def proyecto_display(self, obj):
        """Muestra el proyecto con link"""
        if obj.proyecto:
            return format_html(
                '<a href="/admin/proyectos/proyecto/{}/change/">{}</a>',
                obj.proyecto.id,
                obj.proyecto.codigo
            )
        return "Sin proyecto"
    proyecto_display.short_description = 'Proyecto'
    proyecto_display.admin_order_field = 'proyecto__codigo'
    
    def proyecto_id_display(self, obj):
        """Muestra el ID del proyecto"""
        if obj.proyecto:
            # Opción 1: Solo el ID
            return f"ID: {obj.proyecto.id}"
            
            # Opción 2: Con link al proyecto (alternativa)
            # return format_html(
            #     '<a href="/admin/proyectos/proyecto/{}/change/">{}</a>',
            #     obj.proyecto.id,
            #     obj.proyecto.id
            # )
        return "Sin proyecto"
    proyecto_id_display.short_description = 'ID Proyecto'
    proyecto_id_display.admin_order_field = 'proyecto__id'  # Permite ordenar por ID del proyecto
    
    def descripcion_truncada(self, obj):
        """Muestra descripción truncada"""
        if obj.descripcion:
            return obj.descripcion[:100] + ("..." if len(obj.descripcion) > 100 else "")
        return "Sin descripción"
    descripcion_truncada.short_description = 'Descripción'
    
    def has_supuestos(self, obj):
        """Indica si tiene supuestos"""
        return "✅" if obj.supuestos else "❌"
    has_supuestos.short_description = 'Supuestos'
    has_supuestos.admin_order_field = 'supuestos'
    
    def has_riesgos(self, obj):
        """Indica si tiene riesgos"""
        return "✅" if obj.riesgos else "❌"
    has_riesgos.short_description = 'Riesgos'
    has_riesgos.admin_order_field = 'riesgos'
    
    # Acción personalizada (opcional)
    actions = ['generar_codigo_automatico']
    
    def generar_codigo_automatico(self, request, queryset):
        """Genera código automático para objetivos sin código"""
        for objetivo in queryset.filter(codigo__isnull=True):
            if objetivo.proyecto:
                objetivo.codigo = f"OBJ-{objetivo.proyecto.codigo}"
                objetivo.save()
        
        self.message_user(
            request, 
            f"Códigos generados para {queryset.count()} objetivos."
        )
    generar_codigo_automatico.short_description = "Generar código automático"


from django.contrib import admin
from django.utils.html import format_html
from .models import ObjetivoEspecificoProyecto

@admin.register(ObjetivoEspecificoProyecto)
class ObjetivoEspecificoProyectoAdmin(admin.ModelAdmin):
    """Admin para Objetivo Específico del Proyecto"""
    
    # Campos a mostrar en la lista
    list_display = [
        'id',
        'codigo_display',
        'proyecto_display',
        'proyecto_id_display',
        'objetivo_general_display',
        'objetivo_general_id_display',
        'descripcion_truncada',
        'has_supuestos',
        'has_riesgos',
    ]
    
    # Campos para buscar
    search_fields = [
        'codigo',
        'descripcion',
        'proyecto__codigo',
        'proyecto__nombre',
        'proyecto__id',
        'objetivo_general__codigo',
        'objetivo_general__descripcion',
        'objetivo_general__id',
    ]
    
    # Filtros en la barra lateral
    list_filter = [
        'proyecto__estado',
        'proyecto',
        'objetivo_general',
    ]
    
    # Campos de solo lectura
    readonly_fields = ['codigo', 'proyecto', 'objetivo_general']
    
    # Organización de campos en el formulario de edición
    fieldsets = (
        ('Información Básica', {
            'fields': ('proyecto', 'objetivo_general', 'codigo')
        }),
        ('Descripción del Objetivo', {
            'fields': ('descripcion',)
        }),
        ('Consideraciones', {
            'fields': ('supuestos', 'riesgos'),
            'classes': ('collapse',),
        }),
    )
    
    # Campos para ordenar
    ordering = ['proyecto__codigo', 'objetivo_general__codigo', 'codigo']
    
    # Campos de autocompletar
    autocomplete_fields = ['proyecto', 'objetivo_general']
    
    def codigo_display(self, obj):
        """Muestra el código con formato"""
        return f"OE-{obj.codigo}" if obj.codigo else "Sin código"
    codigo_display.short_description = 'Código'
    codigo_display.admin_order_field = 'codigo'
    
    def proyecto_display(self, obj):
        """Muestra el proyecto con link"""
        if obj.proyecto:
            return format_html(
                '<a href="/admin/proyectos/proyecto/{}/change/">{}</a>',
                obj.proyecto.id,
                obj.proyecto.codigo
            )
        return "Sin proyecto"
    proyecto_display.short_description = 'Proyecto'
    proyecto_display.admin_order_field = 'proyecto__codigo'
    
    def proyecto_id_display(self, obj):
        """Muestra el ID del proyecto"""
        if obj.proyecto:
            return f"ID: {obj.proyecto.id}"
        return "Sin proyecto"
    proyecto_id_display.short_description = 'ID Proy'
    proyecto_id_display.admin_order_field = 'proyecto__id'
    
    def objetivo_general_display(self, obj):
        """Muestra el objetivo general con link"""
        if obj.objetivo_general:
            return format_html(
                '<a href="/admin/proyectos/objetivogeneralproyecto/{}/change/">{}</a>',
                obj.objetivo_general.id,
                obj.objetivo_general.codigo or f"OG-{obj.objetivo_general.id}"
            )
        return "Sin objetivo general"
    objetivo_general_display.short_description = 'Objetivo General'
    objetivo_general_display.admin_order_field = 'objetivo_general__codigo'
    
    def objetivo_general_id_display(self, obj):
        """Muestra el ID del objetivo general"""
        if obj.objetivo_general:
            return f"ID: {obj.objetivo_general.id}"
        return "Sin OG"
    objetivo_general_id_display.short_description = 'ID OG'
    objetivo_general_id_display.admin_order_field = 'objetivo_general__id'
    
    def descripcion_truncada(self, obj):
        """Muestra descripción truncada"""
        if obj.descripcion:
            return obj.descripcion[:80] + ("..." if len(obj.descripcion) > 80 else "")
        return "Sin descripción"
    descripcion_truncada.short_description = 'Descripción'
    
    def has_supuestos(self, obj):
        """Indica si tiene supuestos"""
        return "✅" if obj.supuestos else "❌"
    has_supuestos.short_description = 'Supuestos'
    has_supuestos.admin_order_field = 'supuestos'
    
    def has_riesgos(self, obj):
        """Indica si tiene riesgos"""
        return "✅" if obj.riesgos else "❌"
    has_riesgos.short_description = 'Riesgos'
    has_riesgos.admin_order_field = 'riesgos'
    
    # Acciones personalizadas
    actions = ['generar_codigo_automatico', 'asignar_objetivo_general']
    
    def generar_codigo_automatico(self, request, queryset):
        """Genera código automático para objetivos específicos sin código"""
        for objetivo in queryset.filter(codigo__isnull=True):
            if objetivo.proyecto and objetivo.objetivo_general:
                # Formato: PROY-COD-OG-COD-OE-NUM
                proyecto_cod = objetivo.proyecto.codigo or f"PROY{objetivo.proyecto.id}"
                og_cod = objetivo.objetivo_general.codigo or f"OG{objetivo.objetivo_general.id}"
                
                # Contar objetivos específicos existentes para este OG
                count = ObjetivoEspecificoProyecto.objects.filter(
                    objetivo_general=objetivo.objetivo_general
                ).count()
                
                objetivo.codigo = f"OE-{proyecto_cod}-{og_cod}-{count + 1}"
                objetivo.save()
        
        self.message_user(
            request, 
            f"Códigos generados para {queryset.count()} objetivos específicos."
        )
    generar_codigo_automatico.short_description = "Generar código automático"
    
    def asignar_objetivo_general(self, request, queryset):
        """Asigna automáticamente el objetivo general del proyecto"""
        for objetivo in queryset.filter(objetivo_general__isnull=True):
            if objetivo.proyecto and hasattr(objetivo.proyecto, 'objetivo_general'):
                objetivo.objetivo_general = objetivo.proyecto.objetivo_general
                objetivo.save()
        
        self.message_user(
            request,
            f"Objetivo general asignado a {queryset.count()} objetivos específicos."
        )
    asignar_objetivo_general.short_description = "Asignar objetivo general del proyecto"
    
    # Método para mejorar la vista del detalle
    def get_readonly_fields(self, request, obj=None):
        """Define campos de solo lectura dinámicamente"""
        if obj:  # Si estamos editando un objeto existente
            return ['proyecto', 'objetivo_general', 'codigo']
        return []