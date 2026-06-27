# spme_validaciones/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Validacion, 
    ValidacionInformeActividad, 
    ValidacionInformeTarea,
    HistorialValidacion,
    ValidacionSolicitudFondos,
)
from django.urls import reverse
from django.db import models
from django.utils import timezone

# -------------------------------------------------------------------
# ADMIN PARA VALIDACION BASE (SOLO LECTURA)
# -------------------------------------------------------------------
@admin.register(Validacion)
class ValidacionAdmin(admin.ModelAdmin):
    """
    Admin para la clase base Validacion
    """
    list_display = [
        'id',
        'codigoSeguimiento',
        'usuarioValidador',
        'usuarioRedactor',
        'estado_coloreado',
        'versionDocumento',
        'fechaAsignacion_corta',
        'fechaResolucion_corta'
    ]
    
    list_filter = [
        'estado',
        'versionDocumento',
        'fechaAsignacion',
    ]
    
    search_fields = [
        'codigoSeguimiento',
        'usuarioValidador__username',
        'usuarioValidador__email',
        'usuarioRedactor__username',
        'comentarios'
    ]
    
    readonly_fields = [
        'codigoSeguimiento',
        'fechaAsignacion',
        'fechaResolucion',
        'polymorphic_ctype'
    ]
    
    fieldsets = (
        ('Información General', {
            'fields': (
                'codigoSeguimiento',
                ('usuarioValidador', 'usuarioRedactor'),
                ('estado', 'versionDocumento'),
                'comentarios'
            )
        }),
        ('Fechas', {
            'fields': (
                ('fechaAsignacion', 'fechaResolucion'),
            )
        }),
        ('Metadatos', {
            'fields': ('polymorphic_ctype',),
            'classes': ('collapse',)
        }),
    )
    
    def estado_coloreado(self, obj):
        """Muestra el estado con colores"""
        colors = {
            'PENDIENTE': 'orange',
            'APROBADO': 'green',
            'RECHAZADO': 'red',
        }
        color = colors.get(obj.estado, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_coloreado.short_description = 'Estado'
    estado_coloreado.admin_order_field = 'estado'
    
    def fechaAsignacion_corta(self, obj):
        """Fecha en formato corto"""
        return obj.fechaAsignacion.strftime('%d/%m/%Y %H:%M') if obj.fechaAsignacion else '-'
    fechaAsignacion_corta.short_description = 'Asignación'
    fechaAsignacion_corta.admin_order_field = 'fechaAsignacion'
    
    def fechaResolucion_corta(self, obj):
        """Fecha en formato corto"""
        return obj.fechaResolucion.strftime('%d/%m/%Y %H:%M') if obj.fechaResolucion else '-'
    fechaResolucion_corta.short_description = 'Resolución'
    fechaResolucion_corta.admin_order_field = 'fechaResolucion'
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        return super().get_queryset(request).select_related(
            'usuarioValidador', 
            'usuarioRedactor',
            'polymorphic_ctype'
        )


# -------------------------------------------------------------------
# ADMIN PARA VALIDACIONES DE ACTIVIDAD
# -------------------------------------------------------------------
@admin.register(ValidacionInformeActividad)
class ValidacionInformeActividadAdmin(admin.ModelAdmin):
    """
    Admin para validaciones de Informes de Actividad
    """
    list_display = [
        'id',
        'codigoSeguimiento',
        'informe_link',
        'usuarioValidador',
        'estado_coloreado',
        'versionDocumento',
        'fechaAsignacion_corta'
    ]
    
    list_filter = [
        'estado',
        'versionDocumento',
        'fechaAsignacion',
        'informe__actividad'
    ]
    
    search_fields = [
        'codigoSeguimiento',
        'informe__numeroInforme',
        'usuarioValidador__username',
        'comentarios'
    ]
    
    raw_id_fields = ['informe', 'usuarioValidador', 'usuarioRedactor']
    
    readonly_fields = [
        'codigoSeguimiento',
        'fechaAsignacion',
        'fechaResolucion',
        'informe_detalle'
    ]
    
    fieldsets = (
        ('Validación', {
            'fields': (
                'codigoSeguimiento',
                ('usuarioValidador', 'usuarioRedactor'),
                ('estado', 'versionDocumento'),
                'comentarios'
            )
        }),
        ('Informe Relacionado', {
            'fields': (
                'informe',
                'informe_detalle'
            )
        }),
        ('Fechas', {
            'fields': (
                ('fechaAsignacion', 'fechaResolucion'),
            )
        }),
    )
    
    def informe_link(self, obj):
        """Link al informe en admin"""
        url = f"/admin/spme_monitoreo/informeactividadprincipal/{obj.informe.id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.informe.numeroInforme)
    informe_link.short_description = 'Informe'
    informe_link.admin_order_field = 'informe__numeroInforme'
    
    def informe_detalle(self, obj):
        """Muestra detalles del informe"""
        if obj.informe:
            return format_html(
                '<strong>Actividad:</strong> {}<br>'
                '<strong>Objetivo:</strong> {}<br>'
                '<strong>Usuario:</strong> {}',
                obj.informe.actividad.codigo if obj.informe.actividad else '-',
                obj.informe.objetivoActividad[:100] + '...' if obj.informe.objetivoActividad else '-',
                obj.informe.usuario
            )
        return '-'
    informe_detalle.short_description = 'Detalles del Informe'
    
    def estado_coloreado(self, obj):
        """Muestra el estado con colores"""
        colors = {
            'PENDIENTE': 'orange',
            'APROBADO': 'green',
            'RECHAZADO': 'red',
        }
        color = colors.get(obj.estado, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_coloreado.short_description = 'Estado'
    estado_coloreado.admin_order_field = 'estado'
    
    def fechaAsignacion_corta(self, obj):
        """Fecha en formato corto"""
        return obj.fechaAsignacion.strftime('%d/%m/%Y %H:%M') if obj.fechaAsignacion else '-'
    fechaAsignacion_corta.short_description = 'Asignación'
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        return super().get_queryset(request).select_related(
            'informe',
            'informe__actividad',
            'usuarioValidador',
            'usuarioRedactor'
        )
    
    actions = ['marcar_como_aprobado', 'marcar_como_rechazado']
    
    def marcar_como_aprobado(self, request, queryset):
        """Action para aprobar validaciones"""
        for v in queryset:
            v.estado = 'APROBADO'
            v.save()
        self.message_user(request, f"{queryset.count()} validaciones marcadas como APROBADAS")
    marcar_como_aprobado.short_description = "Marcar como APROBADO"
    
    def marcar_como_rechazado(self, request, queryset):
        """Action para rechazar validaciones"""
        for v in queryset:
            v.estado = 'RECHAZADO'
            v.save()
        self.message_user(request, f"{queryset.count()} validaciones marcadas como RECHAZADAS")
    marcar_como_rechazado.short_description = "Marcar como RECHAZADO"


# -------------------------------------------------------------------
# ADMIN PARA VALIDACIONES DE TAREA
# -------------------------------------------------------------------
@admin.register(ValidacionInformeTarea)
class ValidacionInformeTareaAdmin(admin.ModelAdmin):
    """
    Admin para validaciones de Informes de Tarea
    """
    list_display = [
        'id',
        'codigoSeguimiento',
        'informe_link',
        'usuarioValidador',
        'estado_coloreado',
        'versionDocumento',
        'fechaAsignacion_corta'
    ]
    
    list_filter = [
        'estado',
        'versionDocumento',
        'fechaAsignacion',
    ]
    
    search_fields = [
        'codigoSeguimiento',
        'informeTarea__numeroInforme',
        'usuarioValidador__username',
        'comentarios'
    ]
    
    raw_id_fields = ['informeTarea', 'usuarioValidador', 'usuarioRedactor']
    
    readonly_fields = [
        'codigoSeguimiento',
        'fechaAsignacion',
        'fechaResolucion',
        'informe_detalle'
    ]
    
    fieldsets = (
        ('Validación', {
            'fields': (
                'codigoSeguimiento',
                ('usuarioValidador', 'usuarioRedactor'),
                ('estado', 'versionDocumento'),
                'comentarios'
            )
        }),
        ('Informe Relacionado', {
            'fields': (
                'informeTarea',
                'informe_detalle'
            )
        }),
        ('Fechas', {
            'fields': (
                ('fechaAsignacion', 'fechaResolucion'),
            )
        }),
    )
    
    def informe_link(self, obj):
        """Link al informe en admin"""
        url = f"/admin/spme_monitoreo/informetareaprincipal/{obj.informeTarea.id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.informeTarea.numeroInforme)
    informe_link.short_description = 'Informe Tarea'
    informe_link.admin_order_field = 'informeTarea__numeroInforme'
    
    def informe_detalle(self, obj):
        """Muestra detalles del informe"""
        if obj.informeTarea:
            return format_html(
                '<strong>Tarea:</strong> {}<br>'
                '<strong>Objetivo:</strong> {}<br>'
                '<strong>Usuario:</strong> {}',
                obj.informeTarea.tarea.codigo if obj.informeTarea.tarea else '-',
                obj.informeTarea.objetivoTarea[:100] + '...' if obj.informeTarea.objetivoTarea else '-',
                obj.informeTarea.usuario
            )
        return '-'
    informe_detalle.short_description = 'Detalles del Informe'
    
    def estado_coloreado(self, obj):
        """Muestra el estado con colores"""
        colors = {
            'PENDIENTE': 'orange',
            'APROBADO': 'green',
            'RECHAZADO': 'red',
        }
        color = colors.get(obj.estado, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_coloreado.short_description = 'Estado'
    
    def fechaAsignacion_corta(self, obj):
        """Fecha en formato corto"""
        return obj.fechaAsignacion.strftime('%d/%m/%Y %H:%M') if obj.fechaAsignacion else '-'
    fechaAsignacion_corta.short_description = 'Asignación'
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        return super().get_queryset(request).select_related(
            'informeTarea',
            'informeTarea__tarea',
            'usuarioValidador',
            'usuarioRedactor'
        )
    
    actions = ['marcar_como_aprobado', 'marcar_como_rechazado']
    
    def marcar_como_aprobado(self, request, queryset):
        """Action para aprobar validaciones"""
        for v in queryset:
            v.estado = 'APROBADO'
            v.save()
        self.message_user(request, f"{queryset.count()} validaciones marcadas como APROBADAS")
    marcar_como_aprobado.short_description = "Marcar como APROBADO"
    
    def marcar_como_rechazado(self, request, queryset):
        """Action para rechazar validaciones"""
        for v in queryset:
            v.estado = 'RECHAZADO'
            v.save()
        self.message_user(request, f"{queryset.count()} validaciones marcadas como RECHAZADAS")
    marcar_como_rechazado.short_description = "Marcar como RECHAZADO"


# -------------------------------------------------------------------
# ADMIN PARA VALIDACIONES DE SOLICITUD DE FONDOS
# -------------------------------------------------------------------
@admin.register(ValidacionSolicitudFondos)
class ValidacionSolicitudFondosAdmin(admin.ModelAdmin):
    """
    Admin para validaciones de Solicitudes de Fondos
    """
    list_display = [
        'id',
        'codigoSeguimiento',
        'solicitud_link',
        'usuarioValidador',
        'estado_coloreado',
        'versionDocumento',
        'fechaAsignacion_corta'
    ]
    
    list_filter = [
        'estado',
        'versionDocumento',
        'fechaAsignacion',
    ]
    
    search_fields = [
        'codigoSeguimiento',
        'solicitud__numeroFormulario',
        'usuarioValidador__username',
        'comentarios'
    ]
    
    raw_id_fields = ['solicitud', 'usuarioValidador', 'usuarioRedactor']
    
    readonly_fields = [
        'codigoSeguimiento',
        'fechaAsignacion',
        'fechaResolucion',
        'solicitud_detalle'
    ]
    
    fieldsets = (
        ('Validación', {
            'fields': (
                'codigoSeguimiento',
                ('usuarioValidador', 'usuarioRedactor'),
                ('estado', 'versionDocumento'),
                'comentarios'
            )
        }),
        ('Solicitud Relacionada', {
            'fields': (
                'solicitud',
                'solicitud_detalle'
            )
        }),
        ('Fechas', {
            'fields': (
                ('fechaAsignacion', 'fechaResolucion'),
            )
        }),
    )
    
    def solicitud_link(self, obj):
        """Link a la solicitud en admin"""
        url = f"/admin/spme_fondos/solicitudfondos/{obj.solicitud.id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.solicitud.numeroFormulario)
    solicitud_link.short_description = 'Solicitud'
    solicitud_link.admin_order_field = 'solicitud__numeroFormulario'
    
    def solicitud_detalle(self, obj):
        """Muestra detalles de la solicitud"""
        if obj.solicitud:
            return format_html(
                '<strong>Formulario:</strong> {}<br>'
                '<strong>Monto:</strong> {:,.2f}<br>'
                '<strong>Tipo:</strong> {}<br>'
                '<strong>Solicitante:</strong> {}',
                obj.solicitud.numeroFormulario or f"SF-{obj.solicitud.id}",
                obj.solicitud.montoSolicitado or 0,
                obj.tipo_solicitud,
                obj.solicitud.usuario if hasattr(obj.solicitud, 'usuario') else '-'
            )
        return '-'
    solicitud_detalle.short_description = 'Detalles de la Solicitud'
    
    def estado_coloreado(self, obj):
        """Muestra el estado con colores"""
        colors = {
            'PENDIENTE': 'orange',
            'APROBADO': 'green',
            'RECHAZADO': 'red',
        }
        color = colors.get(obj.estado, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_coloreado.short_description = 'Estado'
    estado_coloreado.admin_order_field = 'estado'
    
    def fechaAsignacion_corta(self, obj):
        """Fecha en formato corto"""
        return obj.fechaAsignacion.strftime('%d/%m/%Y %H:%M') if obj.fechaAsignacion else '-'
    fechaAsignacion_corta.short_description = 'Asignación'
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        return super().get_queryset(request).select_related(
            'solicitud',
            'usuarioValidador',
            'usuarioRedactor'
        )
    
    actions = ['marcar_como_aprobado', 'marcar_como_rechazado']
    
    def marcar_como_aprobado(self, request, queryset):
        """Action para aprobar validaciones"""
        for v in queryset:
            v.estado = 'APROBADO'
            v.save()
        self.message_user(request, f"{queryset.count()} validaciones marcadas como APROBADAS")
    marcar_como_aprobado.short_description = "Marcar como APROBADO"
    
    def marcar_como_rechazado(self, request, queryset):
        """Action para rechazar validaciones"""
        for v in queryset:
            v.estado = 'RECHAZADO'
            v.save()
        self.message_user(request, f"{queryset.count()} validaciones marcadas como RECHAZADAS")
    marcar_como_rechazado.short_description = "Marcar como RECHAZADO"



# -------------------------------------------------------------------
# ADMIN PARA HISTORIAL
# -------------------------------------------------------------------
@admin.register(HistorialValidacion)
class HistorialValidacionAdmin(admin.ModelAdmin):
    """
    Admin para historial de validaciones (solo lectura)
    """
    list_display = [
        'id',
        'validacion_codigo',
        'tipo_documento',
        'usuario',
        'cambio_estado',
        'versionDocumento',
        'fechaCambio_corta'
    ]
    
    list_filter = [
        'fechaCambio',
        'estado_nuevo',
        'versionDocumento'
    ]
    
    search_fields = [
        'validacion__codigoSeguimiento',
        'usuario__username',
        'comentario'
    ]
    
    readonly_fields = [
        'validacion',
        'usuario',
        'estado_anterior',
        'estado_nuevo',
        'versionDocumento',
        'comentario',
        'fechaCambio',
        'validacion_detalle'
    ]
    
    fieldsets = (
        ('Información del Cambio', {
            'fields': (
                'validacion',
                'validacion_detalle',
                'usuario',
                ('estado_anterior', 'estado_nuevo'),
                'versionDocumento',
                'comentario',
                'fechaCambio'
            )
        }),
    )
    
    def validacion_codigo(self, obj):
        """Código de la validación"""
        return obj.validacion.codigoSeguimiento
    validacion_codigo.short_description = 'Validación'
    validacion_codigo.admin_order_field = 'validacion__codigoSeguimiento'
    
    def tipo_documento(self, obj):
        """Tipo de documento"""
        if hasattr(obj.validacion, 'informe'):
            return 'Actividad'
        elif hasattr(obj.validacion, 'informeTarea'):
            return 'Tarea'
        return '-'
    tipo_documento.short_description = 'Tipo'
    
    def cambio_estado(self, obj):
        """Muestra el cambio de estado con flecha"""
        return format_html(
            '{} → {}',
            obj.get_estado_anterior_display() or 'N/A',
            obj.get_estado_nuevo_display()
        )
    cambio_estado.short_description = 'Cambio'
    
    def fechaCambio_corta(self, obj):
        """Fecha en formato corto con zona horaria local"""
        if obj.fechaCambio:
            # Convierte automáticamente a la zona horaria configurada en TIME_ZONE
            local_time = timezone.localtime(obj.fechaCambio)
            return local_time.strftime('%d/%m/%Y %H:%M')
        return '-'
    fechaCambio_corta.short_description = 'Fecha'
    fechaCambio_corta.admin_order_field = 'fechaCambio'
    
    def validacion_detalle(self, obj):
        """Detalle de la validación"""
        v = obj.validacion
        if hasattr(v, 'informe'):
            return format_html(
                'Informe: {}<br>Validador: {}<br>Redactor: {}',
                v.informe.numeroInforme,
                v.usuarioValidador,
                v.usuarioRedactor
            )
        elif hasattr(v, 'informeTarea'):
            return format_html(
                'Informe: {}<br>Validador: {}<br>Redactor: {}',
                v.informeTarea.numeroInforme,
                v.usuarioValidador,
                v.usuarioRedactor
            )
        return '-'
    validacion_detalle.short_description = 'Detalle de Validación'
    
    def has_add_permission(self, request):
        """No permitir crear historial manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """No permitir editar historial"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar historial"""
        return False
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        return super().get_queryset(request).select_related(
            'validacion',
            'usuario'
        )