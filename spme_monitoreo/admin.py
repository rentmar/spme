from django.contrib import admin
from .models import (
    SolicitudFondos, 
    RendicionCuentas, 
    SolicitudReembolso, 
    SolicitudViaje, 
    SolicitudPagoDirecto, 
    FormaPago, 
    InformeActividad, 
    InfActividad, 
    InfTarea
    )
from .models import (
    SolicitudFondosActPei,
    RendicionCuentasActPei,
    SolicitudReembolsoActPei,
    SolicitudViajeActPei,
    SolicitudPagoDirectoActPei,
    InformeActividadPrincipal
)
from django.utils.html import format_html

from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import SolicitudPagoDirecto
import json


#Formas de pago
admin.site.register(FormaPago)

#Solicitudes proyecto
#admin.site.register(RendicionCuentas)
#admin.site.register(SolicitudReembolso)
#admin.site.register(SolicitudPagoDirecto)


#SOLICITUDES DEL PEI
admin.site.register(SolicitudFondosActPei)
admin.site.register(RendicionCuentasActPei)
admin.site.register(SolicitudReembolsoActPei)
admin.site.register(SolicitudViajeActPei)
admin.site.register(SolicitudPagoDirectoActPei)

#Informes de actividad
#admin.site.register(InformeActividad)
admin.site.register(InfActividad)
admin.site.register(InfTarea)

admin.site.register(InformeActividadPrincipal)


@admin.register(SolicitudFondos)
class SolicitudFondosAdmin(admin.ModelAdmin):
    # Campos a mostrar en la lista - ahora con solicitante
    list_display = [
        'numeroFormulario',
        'fechaSolicitud',
        'montoSolicitado',
        'get_solicitante_display',  # Método personalizado
        'estado_validacion',
        'fechaRealizacionActividad',
    ]
    
    # Campos por los que se puede buscar
    search_fields = [
        'numeroFormulario',
        'usuario__username',
        'usuario__first_name',
        'usuario__last_name',
        'descripcion_actividad',
        'objetivo_actividad',
    ]
    
    # Filtros en la barra lateral
    list_filter = [
        'fechaSolicitud',
        'validacionResponsable',
        'validacionCoordinador',
        'formaPago',
    ]
    
    # Campos de solo lectura
    readonly_fields = [
        'numeroFormulario',
        # Solo incluir 'created_at' y 'updated_at' si existen en tu modelo
    ]
    
    # Campos a mostrar en el formulario de edición
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'numeroFormulario',
                'fechaSolicitud',
                'montoSolicitado',
                'lugarSolicitud',
            )
        }),
        ('Información del Solicitante', {  # Nuevo fieldset
            'fields': (
                'usuario',  # En el formulario sigue siendo 'usuario'
            )
        }),
        ('Información de Actividad', {
            'fields': (
                'actividad',
                'tarea',
                'fechaRealizacionActividad',
                'descripcion_actividad',
                'objetivo_actividad',
            )
        }),
        ('Información de Pago', {
            'fields': (
                'formaPago',
                'detalleDestinoFondos',
                'datos_forma_pago',
            )
        }),
        ('Validaciones', {
            'fields': (
                'validacionResponsable',
                'contador',
                'validacionCoordinador',
                'coordinador',
            )
        }),
        ('Configuración', {
            'fields': (
                'bloquearIconosSolFondos',
            )
        }),
    )
    
    # Ordenamiento por defecto
    ordering = ['-fechaSolicitud', '-id']
    
    # Campos por los que se puede hacer clic para editar
    list_display_links = ['numeroFormulario']
    
    # Paginación
    list_per_page = 20
    
    # Método personalizado para mostrar estado de validación
    def estado_validacion(self, obj):
        if obj.validacionResponsable and obj.validacionCoordinador:
            return format_html('<span style="color: green; font-weight: bold;">✓ Completada</span>')
        elif obj.validacionResponsable or obj.validacionCoordinador:
            return format_html('<span style="color: orange; font-weight: bold;">● Parcial</span>')
        else:
            return format_html('<span style="color: red; font-weight: bold;">✗ Pendiente</span>')
    
    estado_validacion.short_description = 'Estado Validación'
    
    # Método personalizado para mostrar "solicitante" en lugar de "usuario"
    def get_solicitante_display(self, obj):
        if obj.usuario:
            # Muestra nombre completo si está disponible
            nombre_completo = f"{obj.usuario.nombre} {obj.usuario.paterno}".strip()
            if nombre_completo:
                return nombre_completo
            return obj.usuario.username
        return "Sin solicitante"
    
    get_solicitante_display.short_description = 'Solicitante'  # Cambia el nombre de la columna
    get_solicitante_display.admin_order_field = 'usuario'  # Permite ordenar por usuario
    
    # Opcional: Cambiar el nombre del campo en el form de admin
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "usuario":
            db_field.verbose_name = "Solicitante"
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    


from django.contrib import admin
from .models import SolicitudPagoDirecto

@admin.register(SolicitudPagoDirecto)
class SolicitudPagoDirectoAdmin(admin.ModelAdmin):
    # Campos a mostrar en la lista principal
    list_display = [
        'id',
        'numeroFormulario',
        'descripcion_actividad',
        'lugarSolicitud',
        'get_actividad_id',
        'get_tarea_id',
        'fechaRealizacionActividad',
        'montoSolicitado',
        'validacionResponsable',
        'validacionCoordinador',
        'usuario',
        'fechaSolicitud'
    ]
    
    # Métodos para obtener los IDs
    def get_actividad_id(self, obj):
        return obj.actividad.id if obj.actividad else '-'
    get_actividad_id.short_description = 'ID Actividad'
    get_actividad_id.admin_order_field = 'actividad__id'
    
    def get_tarea_id(self, obj):
        return obj.tarea.id if obj.tarea else '-'
    get_tarea_id.short_description = 'ID Tarea'
    get_tarea_id.admin_order_field = 'tarea__id'
    
    # Campos para filtrar en la barra lateral
    list_filter = [
        'validacionResponsable',
        'validacionCoordinador',
        'fechaRealizacionActividad',
        'fechaSolicitud',
        'formaPago',
        'bloquearIconosSolFondos'
    ]
    
    # Campos de búsqueda
    search_fields = [
        'numeroFormulario',
        'descripcion_actividad',
        'objetivo_actividad',
        'lugarSolicitud',
        'usuario__username',
        'usuario__email',
        'actividad__id',
        'tarea__id'
    ]


@admin.register(SolicitudReembolso)
class SolicitudReembolsoAdmin(admin.ModelAdmin):
    # Campos a mostrar en la lista principal
    list_display = [
        'id',
        'numeroFormulario',
        'descripcion_corta',
        'lugarSolicitud',
        'get_actividad_id',
        'get_tarea_id',
        'fechaRealizacionActividad',
        'montoSolicitado',
        'validacionResponsable',
        'validacionCoordinador',
        'usuario',
        'fechaSolicitud'
    ]
    
    # Método para descripción corta
    def descripcion_corta(self, obj):
        if obj.descripcion_actividad and len(obj.descripcion_actividad) > 50:
            return f"{obj.descripcion_actividad[:50]}..."
        return obj.descripcion_actividad or '-'
    descripcion_corta.short_description = 'Descripción'
    descripcion_corta.admin_order_field = 'descripcion_actividad'
    
    # Métodos para obtener los IDs
    def get_actividad_id(self, obj):
        return obj.actividad.id if obj.actividad else '-'
    get_actividad_id.short_description = 'ID Actividad'
    get_actividad_id.admin_order_field = 'actividad__id'
    
    def get_tarea_id(self, obj):
        return obj.tarea.id if obj.tarea else '-'
    get_tarea_id.short_description = 'ID Tarea'
    get_tarea_id.admin_order_field = 'tarea__id'
    
    # Campos para filtrar en la barra lateral
    list_filter = [
        'validacionResponsable',
        'validacionCoordinador',
        'fechaRealizacionActividad',
        'fechaSolicitud',
        'formaPago',
        'bloquearIconos'
    ]
    
    # Campos de búsqueda
    search_fields = [
        'numeroFormulario',
        'descripcion_actividad',
        'objetivo_actividad',
        'lugarSolicitud',
        'usuario__username',
        'usuario__email',
        'actividad__id',
        'tarea__id'
    ]
    
    # Campos de solo lectura
    readonly_fields = ['numeroFormulario', 'fechaSolicitud']
    
    # Campos para ordenar
    ordering = ['-fechaSolicitud', '-id']

@admin.register(RendicionCuentas)
class RendicionCuentasAdmin(admin.ModelAdmin):
    # Campos a mostrar en la lista principal
    list_display = [
        'id',
        'numeroFormulario',
        'get_actividad_id',
        'get_tarea_id',
        'fechaActividad',
        'fechaRendicion',
        'montoAsignado',
        'montoDescargado',
        'saldo',
        'usuario',
        'estado_validaciones',
        'tipo_solicitud'
    ]
    
    # Métodos para obtener los IDs
    def get_actividad_id(self, obj):
        return obj.actividad.id if obj.actividad else '-'
    get_actividad_id.short_description = 'ID Actividad'
    get_actividad_id.admin_order_field = 'actividad__id'
    
    def get_tarea_id(self, obj):
        return obj.tarea.id if obj.tarea else '-'
    get_tarea_id.short_description = 'ID Tarea'
    get_tarea_id.admin_order_field = 'tarea__id'
    
    # Método para mostrar estado de validaciones
    def estado_validaciones(self, obj):
        validaciones = []
        if obj.validacionResponsable:
            validaciones.append('Resp')
        if obj.validacionCoordinador:
            validaciones.append('Coord')
        if obj.validacionContador:
            validaciones.append('Cont')
        if obj.validacionAdministrador:
            validaciones.append('Admin')
        
        if validaciones:
            return ', '.join(validaciones)
        return 'Pendiente'
    estado_validaciones.short_description = 'Validaciones'
    
    # Método para mostrar tipo de solicitud
    def tipo_solicitud(self, obj):
        if obj.solicitudFondos:
            return 'Fondos'
        elif obj.solicitudReembolso:
            return 'Reembolso'
        elif obj.solicitudViaje:
            return 'Viaje'
        elif obj.solicitudPagoDirecto:
            return 'Pago Directo'
        return '-'
    tipo_solicitud.short_description = 'Tipo Solicitud'
    
    # Campos para filtrar en la barra lateral
    list_filter = [
        'validacionResponsable',
        'validacionCoordinador',
        'validacionContador',
        'validacionAdministrador',
        'fechaActividad',
        'fechaRendicion',
        'bloquearIconos'
    ]
    
    # Campos de búsqueda
    search_fields = [
        'numeroFormulario',
        'cpteDiario',
        'descripcionActividad',
        'lugarActividad',
        'lugarRendicion',
        'usuario__username',
        'usuario__email',
        'actividad__id',
        'tarea__id',
        'solicitudFondos__numeroFormulario',
        'solicitudReembolso__numeroFormulario',
        'solicitudViaje__numeroFormulario',
        'solicitudPagoDirecto__numeroFormulario'
    ]
    
    # Campos de solo lectura
    readonly_fields = ['numeroFormulario', 'fechaRendicion', 'saldo']
    
    # Campos para ordenar
    ordering = ['-fechaRendicion', '-id']    