from django.contrib import admin
from .models import *
from django.utils.html import format_html
 

# Register your models here.
admin.site.register(InstanciaGestora)
admin.site.register(ProcedenciaFondos)
#admin.site.register(DiagramaEstructura)
#admin.site.register(Proyecto)
admin.site.register(IndicadorProyecto)
#admin.site.register(IndicadorObjetivoGeneral)
# admin.site.register(IndicadorObjetivoEspecifico)
#admin.site.register(IndicadorResultadoObjGral)
#admin.site.register(IndicadorResultadoObjEspecifico)
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
        'esta_habilitado',
        'creado_por',    # mostrar nombre en lugar de CharField plano
        'propietario',       # FK a Usuario
        'get_instancias',    # mostrar todas las IGs relacionadas
        'estado',
        'fecha_inicio',
        'fecha_finalizacion',
    )

    # Filtros laterales
    list_filter = ('estado', 'esta_habilitado', 'instancia_gestora', 'propietario')

    # Búsqueda por campos clave
    search_fields = ('codigo', 'titulo', 'creado_por', 'propietario__username')

    # Campos que se pueden editar directamente desde la lista
    list_editable = ('estado', 'esta_habilitado', 'propietario',)

    save_on_top = True


    # Orden por defecto
    ordering = ('-fecha_creacion',)

    # Campos de solo lectura
    readonly_fields = ('fecha_creacion',)

    # Muestra de campos ManyToMany
    filter_horizontal = ('instancia_gestora', 'procedencia_fondos')

    #Acciones personalizadas
    actions = ['habilitar_proyectos', 'deshabilitar_proyectos']

    def get_instancias(self, obj):
        """
        Muestra las Instancias Gestoras asociadas como lista
        """
        return ", ".join([ig.__str__() for ig in obj.instancia_gestora.all()])
    get_instancias.short_description = "Instancia(s) Gestora(s)"

    @admin.action(description="✅ Habilitar proyectos seleccionados")
    def habilitar_proyectos(self, request, queryset):
        """Acción para habilitar proyectos"""
        actualizados = queryset.update(esta_habilitado=True)
        self.message_user(
            request,
            f"✅ {actualizados} proyecto(s) habilitado(s) exitosamente."
        )
    
    @admin.action(description="❌ Deshabilitar proyectos seleccionados")
    def deshabilitar_proyectos(self, request, queryset):
        """Acción para deshabilitar proyectos"""
        actualizados = queryset.update(esta_habilitado=False)
        self.message_user(
            request,
            f"❌ {actualizados} proyecto(s) deshabilitado(s) exitosamente."
        )


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
        'propietario__username',
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
    

# 📁 admin.py
#from django.contrib import admin
#from .models import IndicadorObjetivoGeneral

@admin.register(IndicadorObjetivoGeneral)
class IndicadorObjetivoGeneralAdmin(admin.ModelAdmin):
    # 📌 Lo básico para ver y editar
    list_display = ['id', 'codigo', 'objetivo_general', 'tipo', 'frecuencia', 'redaccion']
    list_filter = ['tipo', 'frecuencia', 'redaccion', 'objetivo_general']
    search_fields = ['codigo', 'descripcion']
    
    # 📌 Organización del formulario
    fieldsets = (
        ('📋 IDENTIFICACIÓN', {
            'fields': ('codigo', 'descripcion', 'redaccion', 'fuente_verificacion')
        }),
        ('🎯 RELACIÓN', {
            'fields': ('objetivo_general',)
        }),
        ('📊 CONFIGURACIÓN', {
            'fields': ('tipo', 'frecuencia', 'responsable')
        }),
        ('📈 LÍNEA BASE', {
            'fields': (('baseline', 'fechaLineaBase'),)
        }),
        ('🎯 METAS TRIMESTRALES', {
            'fields': (
                ('target_q1', 'fechaTargetQ1'),
                ('target_q2', 'fechaTargetQ2'),
                ('target_q3', 'fechaTargetQ3'),
                ('target_q4', 'fechaTargetQ4'),
            )
        }),
        ('👥 META POBLACIONAL', {
            'fields': (('target_poblacion', 'fechaTargetPoblacion'),)
        }),
    )
    
    # 📌 Atajos para guardar
    save_on_top = True
    list_per_page = 25    


@admin.register(IndicadorResultadoObjGral)
class IndicadorResultadoObjGralAdmin(admin.ModelAdmin):
    # Campos a mostrar en la lista
    list_display = [
        'id',
        'codigo', 
        'descripcion_corta', 
        'resultado_og', 
        'tipo', 
        'frecuencia',
        'redaccion'
    ]
    
    # Campos por los que se puede buscar
    search_fields = [
        'codigo', 
        'descripcion', 
        'redaccion',
        'resultado_og__nombre'  # Asumiendo que ResultadoOG tiene campo 'nombre'
    ]
    
    # Filtros laterales
    list_filter = [
        'tipo', 
        'frecuencia', 
        'redaccion',
        'fechaLineaBase',
        'fechaTargetPoblacion'
    ]
    
    # Organización de campos en el formulario
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'resultado_og',
                'codigo',
                ('redaccion', 'tipo', 'frecuencia'),
                'descripcion',
                'fuente_verificacion',
            )
        }),
        ('Línea Base', {
            'fields': (
                ('baseline', 'fechaLineaBase'),
            )
        }),
        ('Meta General', {
            'fields': (
                ('target_poblacion', 'fechaTargetPoblacion'),
            )
        }),
        ('Metas Trimestrales', {
            'fields': (
                ('target_q1', 'fechaTargetQ1'),
                ('target_q2', 'fechaTargetQ2'),
                ('target_q3', 'fechaTargetQ3'),
                ('target_q4', 'fechaTargetQ4'),
            )
        }),
    )
    
    # Campos de solo lectura (opcional)
    readonly_fields = []
    
    # Ordenamiento por defecto
    ordering = ['resultado_og', 'codigo']
    
    # Número de elementos por página
    list_per_page = 25
    
    # Permitir edición directa desde la lista
    list_editable = ['tipo', 'frecuencia']
    
    # Función para mostrar una versión corta de la descripción
    def descripcion_corta(self, obj):
        if obj.descripcion and len(obj.descripcion) > 50:
            return obj.descripcion[:50] + '...'
        return obj.descripcion
    descripcion_corta.short_description = 'Descripción'
    
    # Autocompletar para la FK (si es necesario)
    #autocomplete_fields = ['resultado_og']    

@admin.register(IndicadorObjetivoEspecifico)
class IndicadorObjetivoEspecificoAdmin(admin.ModelAdmin):
    """
    Admin para Indicador de Objetivo Específico de Proyecto
    """
    
    # Campos a mostrar en la lista
    list_display = [
        'id',
        'codigo', 
        'descripcion_corta', 
        'objetivo_especifico',
        'proyecto_relacionado',
        'objetivo_general_relacionado',
        'tipo', 
        'frecuencia',
        'redaccion'
    ]
    
    # Campos por los que se puede buscar
    search_fields = [
        'codigo', 
        'descripcion', 
        'redaccion',
        'objetivo_especifico__codigo',
        'objetivo_especifico__descripcion',
        'objetivo_especifico__proyecto__codigo',
        'objetivo_especifico__objetivo_general__codigo'
    ]
    
    # Filtros laterales
    list_filter = [
        'tipo', 
        'frecuencia', 
        'redaccion',
        'fechaLineaBase',
        'fechaTargetPoblacion',
        'objetivo_especifico__proyecto',  # Filtrar por proyecto
        'objetivo_especifico__objetivo_general'  # Filtrar por objetivo general
    ]
    
    # Organización de campos en el formulario
    fieldsets = (
        ('📋 INFORMACIÓN BÁSICA', {
            'fields': (
                'objetivo_especifico',
                'codigo',
                ('redaccion', 'tipo', 'frecuencia'),
                'descripcion',
                'fuente_verificacion',
            )
        }),
        ('📊 LÍNEA BASE', {
            'fields': (
                ('baseline', 'fechaLineaBase'),
            )
        }),
        ('🎯 META GENERAL', {
            'fields': (
                ('target_poblacion', 'fechaTargetPoblacion'),
            )
        }),
        ('📈 METAS TRIMESTRALES', {
            'fields': (
                ('target_q1', 'fechaTargetQ1'),
                ('target_q2', 'fechaTargetQ2'),
                ('target_q3', 'fechaTargetQ3'),
                ('target_q4', 'fechaTargetQ4'),
            )
        }),
        ('👤 RESPONSABLE', {
            'fields': ('responsable',),
            'classes': ('collapse',),  # Sección colapsable
        }),
    )
    
    # Campos de solo lectura (opcional)
    readonly_fields = []
    
    # Ordenamiento por defecto
    ordering = ['objetivo_especifico__proyecto', 'objetivo_especifico', 'codigo']
    
    # Número de elementos por página
    list_per_page = 25
    
    # Permitir edición directa desde la lista
    list_editable = ['tipo', 'frecuencia']
    
    # Autocompletar para la FK
    autocomplete_fields = ['objetivo_especifico']
    
    # Acciones personalizadas
    actions = [
        'generar_codigo_automatico', 
        'copiar_metas_del_objetivo',
        'marcar_como_prioritario'
    ]
    
    # Funciones para mostrar información adicional
    def descripcion_corta(self, obj):
        """Muestra descripción truncada"""
        if obj.descripcion and len(obj.descripcion) > 50:
            return obj.descripcion[:50] + '...'
        return obj.descripcion
    descripcion_corta.short_description = 'Descripción'
    descripcion_corta.admin_order_field = 'descripcion'
    
    def proyecto_relacionado(self, obj):
        """Muestra el proyecto relacionado a través del objetivo específico"""
        if obj.objetivo_especifico and obj.objetivo_especifico.proyecto:
            return format_html(
                '<a href="/admin/proyectos/proyecto/{}/change/">{}</a>',
                obj.objetivo_especifico.proyecto.id,
                obj.objetivo_especifico.proyecto.codigo
            )
        return "Sin proyecto"
    proyecto_relacionado.short_description = 'Proyecto'
    proyecto_relacionado.admin_order_field = 'objetivo_especifico__proyecto__codigo'
    
    def objetivo_general_relacionado(self, obj):
        """Muestra el objetivo general relacionado"""
        if obj.objetivo_especifico and obj.objetivo_especifico.objetivo_general:
            return format_html(
                '<a href="/admin/proyectos/objetivogeneralproyecto/{}/change/">{}</a>',
                obj.objetivo_especifico.objetivo_general.id,
                obj.objetivo_especifico.objetivo_general.codigo or "OG"
            )
        return "Sin OG"
    objetivo_general_relacionado.short_description = 'Objetivo General'
    objetivo_general_relacionado.admin_order_field = 'objetivo_especifico__objetivo_general__codigo'
    
    def get_indicadores_relacionados(self, obj):
        """Muestra indicadores relacionados del mismo objetivo"""
        if obj.objetivo_especifico:
            count = IndicadorObjetivoEspecifico.objects.filter(
                objetivo_especifico=obj.objetivo_especifico
            ).count()
            return f"{count} indicador(es)"
        return "N/A"
    get_indicadores_relacionados.short_description = 'Total indicadores del OE'
    
    # Acciones personalizadas
    def generar_codigo_automatico(self, request, queryset):
        """Genera código automático para indicadores sin código"""
        generados = 0
        for indicador in queryset.filter(codigo__isnull=True):
            if indicador.objetivo_especifico:
                # Formato: IND-OE-[PROY]-[OE]-[NRO]
                proyecto_cod = indicador.objetivo_especifico.proyecto.codigo or "PROY"
                oe_cod = indicador.objetivo_especifico.codigo or "OE"
                
                # Contar indicadores existentes para este OE
                count = IndicadorObjetivoEspecifico.objects.filter(
                    objetivo_especifico=indicador.objetivo_especifico
                ).count()
                
                indicador.codigo = f"IND-OE-{proyecto_cod}-{oe_cod}-{count + 1}"
                indicador.save()
                generados += 1
        
        self.message_user(
            request, 
            f"✅ Códigos generados para {generados} indicadores."
        )
    generar_codigo_automatico.short_description = "Generar código automático"
    
    def copiar_metas_del_objetivo(self, request, queryset):
        """Copia las fechas de metas del objetivo específico al indicador"""
        actualizados = 0
        for indicador in queryset:
            if indicador.objetivo_especifico:
                # Aquí puedes definir lógica para copiar metas
                # Por ejemplo, establecer fechas de metas basadas en el proyecto
                if indicador.objetivo_especifico.proyecto:
                    # Copiar fechas del proyecto a las metas del indicador
                    proyecto = indicador.objetivo_especifico.proyecto
                    
                    # Establecer fechas trimestrales basadas en el proyecto
                    # Esto es un ejemplo, ajústalo según tu lógica de negocio
                    indicador.fechaTargetQ1 = proyecto.fecha_inicio
                    indicador.save()
                    actualizados += 1
        
        self.message_user(
            request, 
            f"✅ Metas actualizadas para {actualizados} indicadores."
        )
    copiar_metas_del_objetivo.short_description = "Copiar metas del objetivo"
    
    def marcar_como_prioritario(self, request, queryset):
        """Acción de ejemplo para marcar indicadores (podrías agregar un campo 'prioritario')"""
        # Esta es una acción de ejemplo - necesitarías un campo 'prioritario' en el modelo
        self.message_user(
            request, 
            f"✅ {queryset.count()} indicadores marcados como prioritarios."
        )
    marcar_como_prioritario.short_description = "Marcar como prioritario"
    
    # Personalizar el formulario de edición
    def get_readonly_fields(self, request, obj=None):
        """Define campos de solo lectura según el contexto"""
        if obj:  # Si es edición
            return ['objetivo_especifico']  # No permitir cambiar el OE en edición
        return []
    
    # Personalizar el queryset para incluir información relacionada
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Optimizar consultas con select_related
        return queryset.select_related(
            'objetivo_especifico',
            'objetivo_especifico__proyecto',
            'objetivo_especifico__objetivo_general'
        )
    
    # Agregar botones de guardado en la parte superior
    save_on_top = True
    
    # Configuración de paginación
    list_max_show_all = 200
    show_full_result_count = True
    
    # Campos para vista de detalle
    readonly_fields = ['get_indicadores_relacionados']    

@admin.register(IndicadorResultadoObjEspecifico)
class IndicadorResultadoObjEspecificoAdmin(admin.ModelAdmin):
    """
    Admin para Indicador de Resultado de Objetivo Específico
    """
    
    # Campos a mostrar en la lista
    list_display = [
        'id',
        'codigo', 
        'descripcion_corta', 
        'proyecto_relacionado',
        'tipo', 
        'frecuencia',
        'redaccion',
        'metas_completas',
    ]
    
    # Campos por los que se puede buscar
    search_fields = [
        'codigo', 
        'descripcion', 
    ]
    
    # Filtros laterales
    list_filter = [
        'tipo', 
        'frecuencia', 
        'redaccion',
    ]
    
    # Organización de campos en el formulario
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'codigo',
                ('redaccion', 'tipo', 'frecuencia'),
                'descripcion',
                'fuente_verificacion',
            )
        }),
        ('Línea Base', {
            'fields': (
                ('baseline', 'fechaLineaBase'),
            )
        }),
        ('Metas', {
            'fields': (
                ('target_poblacion', 'fechaTargetPoblacion'),
                ('target_q1', 'fechaTargetQ1'),
                ('target_q2', 'fechaTargetQ2'),
                ('target_q3', 'fechaTargetQ3'),
                ('target_q4', 'fechaTargetQ4'),
            )
        }),
        ('Responsable', {
            'fields': ('responsable',),
            'classes': ('collapse',),
        }),
    )
    
    # Ordenamiento
    ordering = ['codigo']
    
    # Paginación
    list_per_page = 25
    
    # Edición directa desde la lista
    list_editable = ['tipo', 'frecuencia']
    
    # Acciones
    actions = ['exportar_metas_csv']
    
    # Funciones auxiliares
    def descripcion_corta(self, obj):
        if obj.descripcion and len(obj.descripcion) > 50:
            return obj.descripcion[:50] + '...'
        return obj.descripcion
    descripcion_corta.short_description = 'Descripción'
    
    def proyecto_relacionado(self, obj):
        return "Por implementar"
    proyecto_relacionado.short_description = 'Proyecto'
    
    def metas_completas(self, obj):
        """Indica si tiene las 4 metas trimestrales"""
        metas = [obj.target_q1, obj.target_q2, obj.target_q3, obj.target_q4]
        return "✅" if all(metas) else "⚠️"
    metas_completas.short_description = '4/4 Metas'
    
    def exportar_metas_csv(self, request, queryset):
        """Exporta las metas a CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="indicadores_metas.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Código', 'Tipo', 'LB', 'Q1', 'Q2', 'Q3', 'Q4'])
        
        for obj in queryset:
            writer.writerow([
                obj.codigo,
                obj.tipo,
                obj.baseline,
                obj.target_q1,
                obj.target_q2,
                obj.target_q3,
                obj.target_q4,
            ])
        
        return response
    exportar_metas_csv.short_description = "Exportar metas a CSV"
    
    # Botones de guardado arriba
    save_on_top = True


from django.contrib import admin
from .models import ResultadoOG, ResultadoOE

@admin.register(ResultadoOG)
class ResultadoOGAdmin(admin.ModelAdmin):
    list_display = ['id', 'codigo', 'descripcion_corta', 'objetivo_general']
    list_filter = ['objetivo_general']
    search_fields = ['codigo', 'descripcion']
    list_editable = ['codigo']
    list_per_page = 20
    
    fieldsets = (
        ('Información del Resultado', {
            'fields': ('codigo', 'descripcion', 'objetivo_general')
        }),
        ('Gestión de Riesgos', {
            'fields': ('supuestos', 'riesgos'),
            'classes': ('collapse',)
        }),
    )
    
    def descripcion_corta(self, obj):
        return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = 'Descripción (resumen)'


@admin.register(ResultadoOE)
class ResultadoOEAdmin(admin.ModelAdmin):
    list_display = ['id', 'codigo', 'descripcion_corta', 'objetivo_especifico']
    list_filter = ['objetivo_especifico']
    search_fields = ['codigo', 'descripcion']
    list_editable = ['codigo']
    list_per_page = 20
    
    fieldsets = (
        ('Información del Resultado', {
            'fields': ('codigo', 'descripcion', 'objetivo_especifico')
        }),
        ('Gestión de Riesgos', {
            'fields': ('supuestos', 'riesgos'),
            'classes': ('collapse',)
        }),
    )
    
    def descripcion_corta(self, obj):
        return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = 'Descripción (resumen)'

from django.contrib import admin
from .models import DiagramaEstructura

@admin.register(DiagramaEstructura)
class DiagramaEstructuraAdmin(admin.ModelAdmin):
    list_display = ['id', 'codigoProyecto', 'mostrar_id_proyecto', 'proyecto', 'sincronizado', 'creado']
    list_filter = ['sincronizado', 'creado', 'actualizado']
    search_fields = ['codigoProyecto', 'proyecto__titulo']
    list_editable = ['sincronizado']
    readonly_fields = ['creado', 'actualizado']
    list_per_page = 20
    
    def mostrar_id_proyecto(self, obj):
        if obj.proyecto:
            return obj.proyecto.id
        return "-"
    mostrar_id_proyecto.short_description = 'ID Proyecto'
    mostrar_id_proyecto.admin_order_field = 'proyecto__id'  # Permite ordenar por ID
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigoProyecto', 'proyecto', 'sincronizado')
        }),
        ('Estructura del Diagrama', {
            'fields': ('nodos', 'conexiones'),
            'classes': ('wide',),
            'description': 'Formato JSON para nodos y conexiones del diagrama'
        }),
        ('Auditoría', {
            'fields': ('creado', 'actualizado'),
            'classes': ('collapse',)
        }),
    )