from django.contrib import admin
from .models import *
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin


#Pei
admin.site.register(Pei)
admin.site.register(ObjetivoPei)

@admin.register(IndicadorPeiBase)
class IndicadorAdmin(PolymorphicParentModelAdmin):
    base_model = IndicadorPeiBase
    child_models = (IndicadorPeiCualitativo, IndicadorPeiCuantitativo)


@admin.register(IndicadorPeiCuantitativo)
class IndicadorPeiCuantitativoAdmin(PolymorphicChildModelAdmin):
    base_model = IndicadorPeiBase

@admin.register(IndicadorPeiCualitativo)
class IndicadorPeiCualitativoAdmin(PolymorphicChildModelAdmin):
    base_model = IndicadorPeiBase


#Proyectos
admin.site.register(InstanciaGestora)
admin.site.register(Proyecto)