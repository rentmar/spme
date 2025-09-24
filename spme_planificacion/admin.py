from django.contrib import admin
from .models import PlanificacionProyecto, CambioPlanificacion, ProyectoPlan, PlanRevision

# Register your models here.
admin.site.register(PlanificacionProyecto)
admin.site.register(CambioPlanificacion)
#admin.site.register(ProyectoPlan)
#admin.site.register(PlanRevision)