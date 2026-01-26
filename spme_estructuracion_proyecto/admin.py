from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(InstanciaGestora)
admin.site.register(ProcedenciaFondos)
admin.site.register(DiagramaEstructura)
#admin.site.register(Proyecto)
admin.site.register(IndicadorProyecto)
admin.site.register(IndicadorObjetivoGeneral)
admin.site.register(IndicadorObjetivoEspecifico)
admin.site.register(IndicadorResultadoObjGral)
admin.site.register(IndicadorResultadoObjEspecifico)
admin.site.register(ObjetivoGeneralProyecto)
admin.site.register(Proceso)


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    """
    Admin para el modelo Proyecto.
    Muestra información relevante incluyendo:
    - Código y título
    - Creado por (campo legado)
    - Propietario (usuario dueño para permisos)
    - Instancia(s) gestora(s)
    - Estado y fechas
    """

    # Campos que se mostrarán en la lista
    list_display = (
        'codigo',
        'titulo',
        'creado_por',    # mostrar nombre en lugar de CharField plano
        'propietario',       # FK a Usuario
        'get_instancias',    # mostrar todas las IGs relacionadas
        'estado',
        'fecha_inicio',
        'fecha_finalizacion',
    )

    # Filtros laterales
    list_filter = ('estado', 'instancia_gestora', 'propietario')

    # Búsqueda por campos clave
    search_fields = ('codigo', 'titulo', 'creado_por', 'propietario__username')

    # Campos que se pueden editar directamente desde la lista
    list_editable = ('estado', 'propietario',)

    # Orden por defecto
    ordering = ('-fecha_creacion',)

    # Campos de solo lectura
    readonly_fields = ('fecha_creacion',)

    # Muestra de campos ManyToMany
    filter_horizontal = ('instancia_gestora', 'procedencia_fondos')

    def get_instancias(self, obj):
        """
        Muestra las Instancias Gestoras asociadas como lista
        """
        return ", ".join([ig.__str__() for ig in obj.instancia_gestora.all()])
    get_instancias.short_description = "Instancia(s) Gestora(s)"
