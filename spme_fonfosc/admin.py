from django.contrib import admin
from .models import (
    Institucion, 
    ProyectoFonFosc, 
    ObjetivoFonfosc,
    IndicadorObjetivoFonFosc,
    ResultadoFonfosc,
    IndicadorFonFosc,
    DepartamentoBolivia,
    )

# Register your models here.
admin.site.register(ProyectoFonFosc)
admin.site.register(Institucion)
admin.site.register(ObjetivoFonfosc)
admin.site.register(IndicadorObjetivoFonFosc),
admin.site.register(ResultadoFonfosc)
admin.site.register(IndicadorFonFosc)

@admin.register(DepartamentoBolivia)
class DepartamentoBoliviaAdmin(admin.ModelAdmin):
    # Configuración básica
    list_display = ('codigo', 'nombre')
    search_fields = ('codigo', 'nombre')
    ordering = ('nombre',)
    
    # Como solo son 9, mostramos todos en una página
    list_per_page = 10
    
    # Formulario simple
    fields = ('codigo', 'nombre')
    
    # Para que el código se muestre en mayúsculas
    def save_model(self, request, obj, form, change):
        obj.codigo = obj.codigo.upper()
        super().save_model(request, obj, form, change)