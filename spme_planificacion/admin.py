from django.contrib import admin
from .models import PlanificacionProyecto, CambioPlanificacion, ProyectoPlan, PlanRevision, PlanificacionPei

# Register your models here.
admin.site.register(PlanificacionProyecto)
admin.site.register(CambioPlanificacion)
#admin.site.register(ProyectoPlan)
#admin.site.register(PlanRevision)

@admin.register(PlanificacionPei)
class PlanificacionPeiAdmin(admin.ModelAdmin):
    """
    Admin mínimo para PlanificacionPei.
    """
    # Campos a mostrar en la lista
    list_display = ['id', 'pei', 'version', 'creado_el', 'actualizado_el']
    
    # Campos para filtrar
    list_filter = ['version', 'creado_el']
    
    # Campos para buscar
    search_fields = ['pei__titulo']
    
    # Campos de solo lectura
    readonly_fields = ['version', 'creado_el', 'actualizado_el']
    
    
