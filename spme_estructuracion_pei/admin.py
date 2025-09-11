from django.contrib import admin
from .models import Pei, ObjetivoPei, FactoresCriticos, IndicadorPeiCualitativo, IndicadorPeiCuantitativo

# Register your models here.

admin.site.register(Pei)
admin.site.register(ObjetivoPei)
admin.site.register(FactoresCriticos)
admin.site.register(IndicadorPeiCuantitativo)
admin.site.register(IndicadorPeiCualitativo)


