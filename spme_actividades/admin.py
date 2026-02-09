from django.contrib import admin
from .models import Actividad, TareaActividad, TipoActividad
from django.utils.html import format_html


# Register your models here.
#admin.site.register(Actividad)
#admin.site.register(TareaActividad)
#admin.site.register(TipoActividad)


@admin.register(TareaActividad)
class TareaActividadAdmin(admin.ModelAdmin):
    # Campos a mostrar en la lista
    list_display = [
        'id',
        'codigo',
        'titulo',
        'actividad_id',  # Método personalizado
        'actividad_codigo',  # Método personalizado
        'estado',
        'fecha_creacion',
        'fecha_limite',
        'presupuesto',
    ]
    
    # Campos para búsqueda
    search_fields = [
        'codigo',
        'titulo',
        'descripcion',
        'actividad__codigo',  # Buscar por código de actividad
        'actividad__id',  # Buscar por ID de actividad
    ]
    
    # Filtros laterales
    list_filter = [
        'estado',
        'fecha_creacion',
        'fecha_limite',
        'actividad',  # Filtro por actividad (muestra por __str__)
    ]
    
    # Campos de solo lectura
    readonly_fields = [
        'fecha_creacion',
        'actividad_info',  # Método personalizado
    ]
    
    # Campos a mostrar en el formulario de edición
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'codigo',
                'titulo',
                'descripcion',
                'actividad_info',
                'actividad',
            )
        }),
        ('Fechas y Estado', {
            'fields': (
                'estado',
                'fecha_creacion',
                'fecha_ejecucion',
                'fecha_limite',
            )
        }),
        ('Presupuesto', {
            'fields': (
                'presupuesto',
                'presupuestoDesglose',
            ),
            'classes': ('collapse',),  # Sección colapsable
        }),
    )
    
    # Ordenamiento por defecto
    ordering = ['-fecha_creacion']
    
    # Acciones personalizadas
    actions = ['marcar_completadas', 'marcar_en_progreso']
    
    # Método para mostrar ID de actividad
    def actividad_id(self, obj):
        return obj.actividad.id if obj.actividad else None
    actividad_id.short_description = 'ID Actividad'
    actividad_id.admin_order_field = 'actividad__id'
    
    # Método para mostrar código de actividad
    def actividad_codigo(self, obj):
        return obj.actividad.codigo if obj.actividad else 'Sin actividad'
    actividad_codigo.short_description = 'Código Actividad'
    actividad_codigo.admin_order_field = 'actividad__codigo'
    
    # Método para mostrar información completa de la actividad
    def actividad_info(self, obj):
        if obj.actividad:
            return f"ID: {obj.actividad.id} | Código: {obj.actividad.codigo} | Nombre: {obj.actividad.nombre if hasattr(obj.actividad, 'nombre') else 'N/A'}"
        return "Sin actividad asignada"
    actividad_info.short_description = 'Información de Actividad'
    
    # Acción personalizada: Marcar como completadas
    def marcar_completadas(self, request, queryset):
        updated = queryset.update(estado='COMPL')
        self.message_user(request, f'{updated} tarea(s) marcada(s) como completada(s).')
    marcar_completadas.short_description = "Marcar como completadas"
    
    # Acción personalizada: Marcar como en progreso
    def marcar_en_progreso(self, request, queryset):
        updated = queryset.update(estado='EPROG')
        self.message_user(request, f'{updated} tarea(s) marcada(s) como en progreso.')
    marcar_en_progreso.short_description = "Marcar como en progreso"


# Admin para Actividad
class ActividadAdmin(admin.ModelAdmin):
    # Lo que se ve en la lista
    list_display = ('id', 'codigo', 'nombreCorto', 'estado', 'responsable', 'presupuesto')
    
    # Filtros
    list_filter = ('estado', 'tipo', 'estaInactiva')
    
    # Buscar
    search_fields = ('codigo', 'nombreCorto', 'descripcion')
    
    # Campos editables directamente
    list_editable = ('estado',)

# Admin para TareaActividad
class TareaActividadAdmin(admin.ModelAdmin):
    # Lo que se ve en la lista
    list_display = ('codigo', 'titulo', 'actividad', 'estado', 'fecha_ejecucion')
    
    # Filtros
    list_filter = ('estado', 'actividad')
    
    # Buscar
    search_fields = ('codigo', 'titulo', 'descripcion')
    
    # Campos editables
    list_editable = ('estado', 'fecha_ejecucion')

# Registrar los modelos
admin.site.register(Actividad, ActividadAdmin)