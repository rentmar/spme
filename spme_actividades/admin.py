from django.contrib import admin
from .models import Actividad, TareaActividad, TipoActividad
from django.utils.html import format_html


# Register your models here.
#admin.site.register(Actividad)
#admin.site.register(TareaActividad)
#admin.site.register(TipoActividad)

@admin.register(TipoActividad)
class TipoActividadAdmin(admin.ModelAdmin):
    # Campos a mostrar en la lista
    list_display = ('id', 'sigla', 'tipo_actividad')
    
    # Campos por los que se puede buscar
    search_fields = ('sigla', 'tipo_actividad')
    
    # Campos por los que se puede filtrar
    list_filter = ('sigla',)
        
    # Campos visibles en el formulario de edición
    fields = ('sigla', 'tipo_actividad')
    
    # Campos de solo lectura (opcional)
    # readonly_fields = ('sigla',)

from django.contrib import admin
from .models import Actividad, TareaActividad

# Admin para Actividad
class ActividadAdmin(admin.ModelAdmin):
    # Lo que se ve en la lista
    list_display = ('codigo', 'nombreCorto', 'estado', 'responsable', 'presupuesto')
    
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
admin.site.register(TareaActividad, TareaActividadAdmin)