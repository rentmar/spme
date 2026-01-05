from django.contrib import admin
from .models import Pei, ObjetivoPei, FactoresCriticos, IndicadorPeiCualitativo, IndicadorPeiCuantitativo, ActividadPei, TareaActividadPei

# Register your models here.

#admin.site.register(Pei)
admin.site.register(ObjetivoPei)
admin.site.register(FactoresCriticos)
admin.site.register(IndicadorPeiCuantitativo)
admin.site.register(IndicadorPeiCualitativo)
#admin.site.register(ActividadPei)
#admin.site.register(TareaActividadPei)

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
    
    # Campos en formulario
    fields = (
        'codigo',
        'titulo',
        'descripcion',
        'actividad',
        'estado',
        'fecha_ejecucion',
        'fecha_limite',
        'presupuesto'
    )
    
    # Acciones básicas
    actions = ['marcar_como_completadas']
    
    def marcar_como_completadas(self, request, queryset):
        from django.utils import timezone
        queryset.update(estado='COMPL', fecha_ejecucion=timezone.now().date())
        self.message_user(request, f'{queryset.count()} tarea(s) completada(s).')
    marcar_como_completadas.short_description = "Marcar como Completadas"
