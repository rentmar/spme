from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(InstanciaGestora)
admin.site.register(ProcedenciaFondos)
admin.site.register(DiagramaEstructura)
admin.site.register(Proyecto)
admin.site.register(IndicadorProyecto)
admin.site.register(IndicadorObjetivoGeneral)
admin.site.register(IndicadorObjetivoEspecifico)
admin.site.register(IndicadorResultadoObjGral)
admin.site.register(IndicadorResultadoObjEspecifico)
admin.site.register(ObjetivoGeneralProyecto)