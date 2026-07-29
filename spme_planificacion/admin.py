from django.contrib import admin
from .models import PlanificacionProyecto, CambioPlanificacion, ProyectoPlan, PlanRevision, PlanificacionPei
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
from .models import (
    PlanificacionVersion,
    HistorialCambioPlanificacion,
)
# Register your models here.
#admin.site.register(PlanificacionProyecto)
#admin.site.register(CambioPlanificacion)
#admin.site.register(ProyectoPlan)
#admin.site.register(PlanRevision)




@admin.register(PlanificacionVersion)
class PlanificacionVersionAdmin(admin.ModelAdmin):
    list_display = ['id', 'proyecto', 'version_numero', 'usuario', 'timestamp', 'motivo_corto']
    list_filter = ['proyecto', 'usuario']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'

    def motivo_corto(self, obj):
        return obj.motivo[:60] + '...' if len(obj.motivo) > 60 else obj.motivo
    motivo_corto.short_description = 'Motivo'


@admin.register(HistorialCambioPlanificacion)
class HistorialCambioPlanificacionAdmin(PolymorphicChildModelAdmin):
    base_model = HistorialCambioPlanificacion
    list_display = ['id', 'accion_display', 'actividad_codigo', 'actividad_id', 'columna', 'usuario', 'timestamp']
    list_filter = ['accion', 'columna', 'usuario']
    search_fields = ['actividad_codigo', 'actividad_id', 'columna']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'