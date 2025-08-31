from django.contrib import admin
from .models import PlanificacionProyecto, CambioPlanificacion

# Register your models here.
admin.site.register(PlanificacionProyecto)
admin.site.register(CambioPlanificacion)