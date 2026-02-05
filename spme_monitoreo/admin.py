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
#SOLICITUDES DEL PEI
# admin.site.register(SolicitudFondosActPei)
#admin.site.register(RendicionCuentasActPei)
#admin.site.register(SolicitudReembolsoActPei)
#admin.site.register(SolicitudViajeActPei)
#admin.site.register(SolicitudPagoDirectoActPei)

@admin.register(SolicitudFondosActPei)
class SolicitudFondosActPeiAdmin(admin.ModelAdmin):
    # Campos a mostrar en la lista
    list_display = [
        'mostrar_id_solicitud',
        'mostrar_id_actividad',
        'mostrar_id_tarea',
        'numeroFormulario',
        'montoSolicitado',
        'fechaSolicitud',
        'usuario'
    ]
    
    # Campos para búsqueda
    search_fields = [
        'id',
        'numeroFormulario',
        'actividad__id',
        'tarea__id',
        'usuario__username'
    ]
    
    # Campos de solo lectura
    readonly_fields = ['numeroFormulario']
    
    # Para ordenar por defecto por ID
    ordering = ['-id']
    
    # Mostrar más elementos por página
    list_per_page = 50
    
    # Métodos personalizados
    def mostrar_id_solicitud(self, obj):
        return f"ID: {obj.id}"
    mostrar_id_solicitud.short_description = 'ID Solicitud'
    mostrar_id_solicitud.admin_order_field = 'id'
    
    def mostrar_id_actividad(self, obj):
        if obj.actividad:
            return f"ID: {obj.actividad.id}"
        return "Sin actividad"
    mostrar_id_actividad.short_description = 'ID Actividad'
    mostrar_id_actividad.admin_order_field = 'actividad__id'
    
    def mostrar_id_tarea(self, obj):
        if obj.tarea:
            return f"ID: {obj.tarea.id}"
        return "Sin tarea"
    mostrar_id_tarea.short_description = 'ID Tarea'
    mostrar_id_tarea.admin_order_field = 'tarea__id'

@admin.register(SolicitudViajeActPei)
class SolicitudViajeActPeiAdmin(admin.ModelAdmin):
    # Campos a mostrar en la lista
    list_display = [
        'solicitud_id',
        'actividad_id',
        'tarea_id',
        'numeroFormulario',
        'evento',
        'lugarEvento',
        'fechaEvento',
        'montoSolicitado',
        'usuario',
        'bloquearIconos',
        'validacionResponsable',
        'validacionCoordinador'
    ]
    
    # Campos para búsqueda
    search_fields = [
        'id',
        'numeroFormulario',
        'actividad__id',
        'tarea__id',
        'evento',
        'lugarEvento',
        'usuario__username'
    ]
    
    # Filtros en la barra lateral
    list_filter = [
        'validacionResponsable',
        'validacionCoordinador',
        'bloquearIconos',
        'fechaSolicitud',
        'fechaEvento',
        'actividad',
        'tarea'
    ]
    
    # Campos de solo lectura
    readonly_fields = ['numeroFormulario']
    
    # Campos editables en la lista
    list_editable = [
        'bloquearIconos',
        'validacionResponsable',
        'validacionCoordinador'
    ]
    
    # Para ordenar por defecto por ID
    ordering = ['-id']
    
    # Mostrar más elementos por página
    list_per_page = 50
    
    # Métodos personalizados para mostrar IDs
    def solicitud_id(self, obj):
        return obj.id
    solicitud_id.short_description = 'ID'
    solicitud_id.admin_order_field = 'id'
    
    def actividad_id(self, obj):
        return obj.actividad.id if obj.actividad else None
    actividad_id.short_description = 'Actividad ID'
    actividad_id.admin_order_field = 'actividad__id'
    
    def tarea_id(self, obj):
        return obj.tarea.id if obj.tarea else None
    tarea_id.short_description = 'Tarea ID'
    tarea_id.admin_order_field = 'tarea__id'
    
    # Configuración del formulario de edición
    fieldsets = (
        ('Información General', {
            'fields': (
                'numeroFormulario',
                'fechaSolicitud',
                'lugarSolicitud',
                'usuario',
                'actividad',
                'tarea'
            )
        }),
        ('Detalles del Evento', {
            'fields': (
                'evento',
                'lugarEvento',
                'fechaEvento',
                'institucionesParticipantes',
                'organizador',
                'quienCubreGastos',
                'justificacionAsistencia',
                'fondosUnitas',
                'tareasPrevias',
            )
        }),
        ('Información Financiera', {
            'fields': (
                'montoSolicitado',
                'detalleGasto',
                'formaPago',
                'datos_forma_pago',
            )
        }),
        ('Validaciones', {
            'fields': (
                'validacionResponsable',
                'responsable',
                'validacionCoordinador',
                'coordinador',
                'bloquearIconos',
            )
        }),
    )


@admin.register(SolicitudPagoDirectoActPei)
class SolicitudPagoDirectoActPeiAdmin(admin.ModelAdmin):
    # Campos a mostrar en la lista
    list_display = [
        'solicitud_id',
        'actividad_id',
        'tarea_id',
        'numeroFormulario',
        'montoSolicitado',
        'fechaSolicitud',
        'usuario',
        'bloquearIconosSolFondos',
        'validacionResponsable',
        'validacionCoordinador'
    ]
    
    # Campos para búsqueda
    search_fields = [
        'id',
        'numeroFormulario',
        'actividad__id',
        'tarea__id',
        'usuario__username',
        'descripcion_actividad'
    ]
    
    # Filtros en la barra lateral
    list_filter = [
        'validacionResponsable',
        'validacionCoordinador',
        'bloquearIconosSolFondos',
        'fechaSolicitud',
        'fechaRealizacionActividad',
        'actividad',
        'tarea'
    ]
    
    # Campos de solo lectura
    readonly_fields = ['numeroFormulario']
    
    # Campos editables en la lista
    list_editable = [
        'bloquearIconosSolFondos',
        'validacionResponsable',
        'validacionCoordinador'
    ]
    
    # Para ordenar por defecto por ID
    ordering = ['-id']
    
    # Mostrar más elementos por página
    list_per_page = 50
    
    # Métodos personalizados para mostrar IDs
    def solicitud_id(self, obj):
        return obj.id
    solicitud_id.short_description = 'ID'
    solicitud_id.admin_order_field = 'id'
    
    def actividad_id(self, obj):
        return obj.actividad.id if obj.actividad else None
    actividad_id.short_description = 'Actividad ID'
    actividad_id.admin_order_field = 'actividad__id'
    
    def tarea_id(self, obj):
        return obj.tarea.id if obj.tarea else None
    tarea_id.short_description = 'Tarea ID'
    tarea_id.admin_order_field = 'tarea__id'
    
    # Configuración del formulario de edición
    fieldsets = (
        ('Información General', {
            'fields': (
                'numeroFormulario',
                'fechaSolicitud',
                'lugarSolicitud',
                'usuario',
                'actividad',
                'tarea'
            )
        }),
        ('Detalles de la Actividad', {
            'fields': (
                'fechaRealizacionActividad',
                'descripcion_actividad',
                'objetivo_actividad',
            )
        }),
        ('Información Financiera', {
            'fields': (
                'montoSolicitado',
                'detalleDestinoFondos',
                'formaPago',
                'datos_forma_pago',
            )
        }),
        ('Validaciones', {
            'fields': (
                'validacionResponsable',
                'contador',
                'validacionCoordinador',
                'coordinador',
                'bloquearIconosSolFondos',
            )
        }),
    )


@admin.register(SolicitudReembolsoActPei)
class SolicitudReembolsoActPeiAdmin(admin.ModelAdmin):
    # Campos a mostrar en la lista
    list_display = [
        'solicitud_id',
        'actividad_id',
        'tarea_id',
        'numeroFormulario',
        'montoSolicitado',
        'fechaSolicitud',
        'usuario',
        'bloquearIconos',
        'validacionResponsable',
        'validacionCoordinador'
    ]
    
    # Campos para búsqueda
    search_fields = [
        'id',
        'numeroFormulario',
        'actividad__id',
        'tarea__id',
        'usuario__username',
        'descripcion_actividad'
    ]
    
    # Filtros en la barra lateral
    list_filter = [
        'validacionResponsable',
        'validacionCoordinador',
        'bloquearIconos',
        'fechaSolicitud',
        'fechaRealizacionActividad',
        'actividad',
        'tarea'
    ]
    
    # Campos de solo lectura
    readonly_fields = ['numeroFormulario']
    
    # Campos editables en la lista
    list_editable = [
        'bloquearIconos',
        'validacionResponsable',
        'validacionCoordinador'
    ]
    
    # Para ordenar por defecto por ID
    ordering = ['-id']
    
    # Mostrar más elementos por página
    list_per_page = 50
    
    # Métodos personalizados para mostrar IDs
    def solicitud_id(self, obj):
        return obj.id
    solicitud_id.short_description = 'ID'
    solicitud_id.admin_order_field = 'id'
    
    def actividad_id(self, obj):
        return obj.actividad.id if obj.actividad else None
    actividad_id.short_description = 'Actividad ID'
    actividad_id.admin_order_field = 'actividad__id'
    
    def tarea_id(self, obj):
        return obj.tarea.id if obj.tarea else None
    tarea_id.short_description = 'Tarea ID'
    tarea_id.admin_order_field = 'tarea__id'
    
    # Configuración del formulario de edición
    fieldsets = (
        ('Información General', {
            'fields': (
                'numeroFormulario',
                'fechaSolicitud',
                'lugarSolicitud',
                'usuario',
                'actividad',
                'tarea'
            )
        }),
        ('Detalles de la Actividad', {
            'fields': (
                'fechaRealizacionActividad',
                'descripcion_actividad',
                'objetivo_actividad',
            )
        }),
        ('Información Financiera', {
            'fields': (
                'montoSolicitado',
                'detalleDestinoFondos',
                'formaPago',
                'datos_forma_pago',
            )
        }),
        ('Validaciones', {
            'fields': (
                'validacionResponsable',
                'responsable',
                'validacionCoordinador',
                'coordinador',
                'bloquearIconos',
            )
        }),
    )



from django.contrib import admin
from django.utils.html import format_html
from .models import RendicionCuentasActPei

@admin.register(RendicionCuentasActPei)
class RendicionCuentasActPeiAdmin(admin.ModelAdmin):
    # Campos a mostrar en la lista (incluyendo los editables)
    list_display = [
        'solicitud_id',
        'actividad_id',
        'tarea_id',
        'numeroFormulario',
        'montoAsignado',
        'montoDescargado',
        'saldo',
        'usuario',
        'fechaRendicion',
        'tipo_solicitud',
        'estado_validaciones',
        'bloquearIconos',
        'validacionResponsable',
        'validacionCoordinador',
        'validacionContador',
        'validacionAdministrador'
    ]
    
    # Campos para búsqueda
    search_fields = [
        'id',
        'numeroFormulario',
        'actividad__id',
        'tarea__id',
        'usuario__username',
        'cpteDiario',
        'descripcionActividad'
    ]
    
    # Filtros en la barra lateral
    list_filter = [
        'validacionResponsable',
        'validacionCoordinador',
        'validacionContador',
        'validacionAdministrador',
        'bloquearIconos',
        'fechaActividad',
        'fechaRendicion',
        'actividad',
        'tarea'
    ]
    
    # Campos de solo lectura
    readonly_fields = ['numeroFormulario', 'fechaRendicion', 'saldo']
    
    # Campos editables en la lista (deben estar en list_display)
    list_editable = [
        'bloquearIconos',
        'validacionResponsable',
        'validacionCoordinador',
        'validacionContador',
        'validacionAdministrador'
    ]
    
    # Para ordenar por defecto por ID
    ordering = ['-id']
    
    # Mostrar más elementos por página
    list_per_page = 50
    
    # Métodos personalizados para mostrar IDs
    def solicitud_id(self, obj):
        return obj.id
    solicitud_id.short_description = 'ID'
    solicitud_id.admin_order_field = 'id'
    
    def actividad_id(self, obj):
        return obj.actividad.id if obj.actividad else None
    actividad_id.short_description = 'Actividad ID'
    actividad_id.admin_order_field = 'actividad__id'
    
    def tarea_id(self, obj):
        return obj.tarea.id if obj.tarea else None
    tarea_id.short_description = 'Tarea ID'
    tarea_id.admin_order_field = 'tarea__id'
    
    # Método para mostrar tipo de solicitud
    def tipo_solicitud(self, obj):
        if obj.solicitudFondos:
            return 'Fondos PEI'
        elif obj.solicitudReembolso:
            return 'Reembolso PEI'
        elif obj.solicitudViaje:
            return 'Viaje PEI'
        elif obj.solicitudPagoDirecto:
            return 'Pago Directo PEI'
        return 'Sin solicitud'
    tipo_solicitud.short_description = 'Tipo Solicitud'
    
    # Método para mostrar estado de validaciones (solo lectura, no editable)
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
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                'green' if len(validaciones) == 4 else 'orange',
                ', '.join(validaciones)
            )
        return format_html('<span style="color: red; font-weight: bold;">Pendiente</span>')
    estado_validaciones.short_description = 'Validaciones'
    
    # Configuración del formulario de edición
    fieldsets = (
        ('Información General', {
            'fields': (
                'numeroFormulario',
                'fechaRendicion',
                'lugarRendicion',
                'usuario',
                'actividad',
                'tarea'
            )
        }),
        ('Información de la Actividad', {
            'fields': (
                'fechaActividad',
                'descripcionActividad',
                'lugarActividad',
            )
        }),
        ('Información Financiera', {
            'fields': (
                'cpteDiario',
                'fechaDesembolso',
                'montoAsignado',
                'montoDescargado',
                'saldo',
                'detalleDestinoFondos',
            )
        }),
        ('Solicitud Relacionada', {
            'fields': (
                'solicitudFondos',
                'solicitudReembolso',
                'solicitudViaje',
                'solicitudPagoDirecto',
            )
        }),
        ('Validaciones', {
            'fields': (
                'validacionResponsable',
                'responsable',
                'validacionCoordinador',
                'coordinador',
                'validacionContador',
                'contador',
                'validacionAdministrador',
                'administrador',
                'bloquearIconos',
            )
        }),
    )


#Informes de actividad
#admin.site.register(InformeActividad)
admin.site.register(InfActividad)
admin.site.register(InfTarea)

admin.site.register(InformeActividadPrincipal)


@admin.register(SolicitudFondos)
class SolicitudFondosAdmin(admin.ModelAdmin):
    # Campos a mostrar en la lista principal
    list_display = [
        'id',
        'numeroFormulario',
        'get_actividad_id',
        'get_tarea_id',
        'descripcion_corta',
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
    
    # Método para descripción corta
    def descripcion_corta(self, obj):
        if obj.descripcion_actividad and len(obj.descripcion_actividad) > 50:
            return f"{obj.descripcion_actividad[:50]}..."
        return obj.descripcion_actividad or '-'
    descripcion_corta.short_description = 'Descripción'
    descripcion_corta.admin_order_field = 'descripcion_actividad'
    
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
        'tarea__id',
        'contador__username',
        'coordinador__username'
    ]
     
    # Campos de solo lectura
    readonly_fields = ['numeroFormulario', 'fechaSolicitud']
    
    # Campos para ordenar
    ordering = ['-fechaSolicitud', '-id']

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



@admin.register(SolicitudViaje)
class SolicitudViajeAdmin(admin.ModelAdmin):
    # Campos a mostrar en la lista - SOLO IDs NUMÉRICOS
    list_display = [
        'id',  # ID de la solicitud
        'numeroFormulario',
        'fechaSolicitud',
        'evento',
        'actividad_id',  # ID numérico directo
        'tarea_id',      # ID numérico directo
        'get_solicitante_display',
        'montoSolicitado',
        'estado_validacion',
        'fechaEvento',
    ]
    
    # Campos por los que se puede buscar
    search_fields = [
        'numeroFormulario',
        'evento',
        'lugarEvento',
        'organizador',
        'usuario__username',
        'usuario__nombre',
        'usuario__paterno',
        'usuario__materno',
        'id',
    ]
    
    # Filtros en la barra lateral
    list_filter = [
        'fechaSolicitud',
        'fechaEvento',
        'validacionResponsable',
        'validacionCoordinador',
        'formaPago',
        'lugarEvento',
    ]
    
    # Campos de solo lectura
    readonly_fields = [
        'numeroFormulario',
    ]
    
    # Campos a mostrar en el formulario de edición
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'numeroFormulario',
                'fechaSolicitud',
                'lugarSolicitud',
                'montoSolicitado',
            )
        }),
        ('Información del Solicitante', {
            'fields': (
                'usuario',
            )
        }),
        ('Información del Evento', {
            'fields': (
                'evento',
                'lugarEvento',
                'fechaEvento',
                'organizador',
                'institucionesParticipantes',
                'quienCubreGastos',
            )
        }),
        ('Detalles del Viaje', {
            'fields': (
                'justificacionAsistencia',
                'fondosUnitas',
                'tareasPrevias',
                'detalleGasto',
            )
        }),
        ('Información de Pago', {
            'fields': (
                'formaPago',
                'datos_forma_pago',
            )
        }),
        ('Validaciones', {
            'fields': (
                'validacionResponsable',
                'responsable',
                'validacionCoordinador',
                'coordinador',
            )
        }),
        ('Relaciones', {
            'classes': ('collapse',),
            'fields': (
                'actividad',
                'tarea',
            )
        }),
        ('Configuración', {
            'fields': (
                'bloquearIconos',
            )
        }),
    )
    
    # Ordenamiento por defecto
    ordering = ['-fechaSolicitud', '-id']
    
    # Campos por los que se puede hacer clic para editar
    list_display_links = ['id', 'numeroFormulario']
    
    # Paginación
    list_per_page = 20
    
    # ========== MÉTODOS SIMPLES PARA MOSTRAR IDs NUMÉRICOS ==========
    
    # Método para mostrar ID numérico de actividad
    def actividad_id(self, obj):
        return obj.actividad.id if obj.actividad else '-'
    actividad_id.short_description = 'ID Actividad'
    actividad_id.admin_order_field = 'actividad__id'
    
    # Método para mostrar ID numérico de tarea
    def tarea_id(self, obj):
        return obj.tarea.id if obj.tarea else '-'
    tarea_id.short_description = 'ID Tarea'
    tarea_id.admin_order_field = 'tarea__id'
    
    # Método personalizado para mostrar estado de validación
    def estado_validacion(self, obj):
        if obj.validacionResponsable and obj.validacionCoordinador:
            return format_html('<span style="color: green; font-weight: bold;">✓ Aprobado</span>')
        elif obj.validacionResponsable or obj.validacionCoordinador:
            return format_html('<span style="color: orange; font-weight: bold;">● Pendiente</span>')
        else:
            return format_html('<span style="color: red; font-weight: bold;">✗ Por validar</span>')
    estado_validacion.short_description = 'Estado Validación'
    
    # Método personalizado para mostrar "solicitante"
    def get_solicitante_display(self, obj):
        if obj.usuario:
            nombre_completo = f"{obj.usuario.nombre} {obj.usuario.paterno} {obj.usuario.materno}".strip()
            if nombre_completo:
                return nombre_completo
            return obj.usuario.username
        return "Sin solicitante"
    get_solicitante_display.short_description = 'Solicitante'
    get_solicitante_display.admin_order_field = 'usuario'
    
    # Para optimizar las consultas
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'usuario',
            'responsable',
            'coordinador',
            'formaPago',
            'actividad',
            'tarea'
        )