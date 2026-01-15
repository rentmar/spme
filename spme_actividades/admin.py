from django.contrib import admin
from .models import Actividad, TareaActividad, TipoActividad

# Register your models here.
admin.site.register(Actividad)
admin.site.register(TareaActividad)
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