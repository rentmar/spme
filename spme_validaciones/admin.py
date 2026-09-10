# spme_validaciones/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Validacion, 
    ValidacionInformeActividad, 
    ValidacionInformeTarea,
    HistorialValidacion,
    ValidacionSolicitudFondos,
    ValidacionSolicitudViaje,
    ValidacionSolicitudPagoDirecto,
    ValidacionSolicitudReembolso,
    ValidacionRendicionCuentas,
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
        'comentarios',
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
# ADMIN PARA VALIDACIONES DE SOLICITUD DE VIAJE
# -------------------------------------------------------------------
@admin.register(ValidacionSolicitudViaje)
class ValidacionSolicitudViajeAdmin(admin.ModelAdmin):
    """
    Admin para validaciones de Solicitudes de Viaje
    """
    list_display = [
        'id',
        'codigoSeguimiento',
        'solicitud_link',
        'usuarioValidador',
        'estado_coloreado',
        'tipo_solicitud_coloreado',
        'versionDocumento',
        'fechaAsignacion_corta'
    ]
    
    list_filter = [
        'estado',
        'versionDocumento',
        'fechaAsignacion',
        'solicitud__actividad',  # Para filtrar por actividad
    ]
    
    search_fields = [
        'codigoSeguimiento',
        'solicitud__numeroFormulario',
        'usuarioValidador__username',
        'usuarioValidador__first_name',
        'usuarioValidador__last_name',
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
        """Link a la solicitud de viaje en admin"""
        url = f"/admin/spme_viajes/solicitudviaje/{obj.solicitud.id}/change/"
        return format_html('<a href="{}">✈️ {}</a>', url, obj.codigo_solicitud)
    solicitud_link.short_description = 'Solicitud de Viaje'
    solicitud_link.admin_order_field = 'solicitud__numeroFormulario'
    
    def solicitud_detalle(self, obj):
        """Muestra detalles de la solicitud de viaje"""
        if obj.solicitud:
            detalles = []
            
            # Código de formulario
            detalles.append(
                f'<strong>Formulario:</strong> {obj.codigo_solicitud}'
            )
            
            # Tipo de solicitud
            tipo = obj.tipo_solicitud
            tipo_colores = {
                'ACTIVIDAD': '#3498db',
                'TAREA': '#9b59b6',
                'GENERAL': '#95a5a6'
            }
            color_tipo = tipo_colores.get(tipo, '#95a5a6')
            detalles.append(
                f'<strong>Tipo:</strong> <span style="color: {color_tipo}; font-weight: bold;">{tipo}</span>'
            )
            
            # Monto
            detalles.append(
                f'<strong>Monto:</strong> {obj.monto_solicitud:,.2f}' if obj.monto_solicitud else '<strong>Monto:</strong> -'
            )
            
            # Actividad o Tarea relacionada
            if obj.solicitud.actividad:
                detalles.append(
                    f'<strong>Actividad:</strong> {obj.solicitud.actividad}'
                )
            if obj.solicitud.tarea:
                detalles.append(
                    f'<strong>Tarea:</strong> {obj.solicitud.tarea}'
                )
            
            # Solicitante
            if hasattr(obj.solicitud, 'usuario') and obj.solicitud.usuario:
                detalles.append(
                    f'<strong>Solicitante:</strong> {obj.solicitud.usuario.get_full_name() or obj.solicitud.usuario.username}'
                )
            
            # Destino si existe
            if hasattr(obj.solicitud, 'destino') and obj.solicitud.destino:
                detalles.append(
                    f'<strong>Destino:</strong> {obj.solicitud.destino}'
                )
            
            # Fechas del viaje si existen
            if hasattr(obj.solicitud, 'fechaInicio') and obj.solicitud.fechaInicio:
                fecha_fin = obj.solicitud.fechaFin if hasattr(obj.solicitud, 'fechaFin') and obj.solicitud.fechaFin else None
                if fecha_fin:
                    detalles.append(
                        f'<strong>Viaje:</strong> {obj.solicitud.fechaInicio.strftime("%d/%m/%Y")} - {fecha_fin.strftime("%d/%m/%Y")}'
                    )
                else:
                    detalles.append(
                        f'<strong>Fecha:</strong> {obj.solicitud.fechaInicio.strftime("%d/%m/%Y")}'
                    )
            
            return format_html('<br>'.join(detalles))
        return '-'
    solicitud_detalle.short_description = 'Detalles de la Solicitud'
    
    def tipo_solicitud_coloreado(self, obj):
        """Muestra el tipo de solicitud con colores"""
        tipo = obj.tipo_solicitud
        colores = {
            'ACTIVIDAD': '#3498db',  # Azul
            'TAREA': '#9b59b6',      # Púrpura
            'GENERAL': '#95a5a6'     # Gris
        }
        iconos = {
            'ACTIVIDAD': '📋',
            'TAREA': '✅',
            'GENERAL': '📄'
        }
        color = colores.get(tipo, '#95a5a6')
        icono = iconos.get(tipo, '📄')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            icono,
            tipo
        )
    tipo_solicitud_coloreado.short_description = 'Tipo'
    
    def estado_coloreado(self, obj):
        """Muestra el estado con colores"""
        colors = {
            'PENDIENTE': 'orange',
            'APROBADO': 'green',
            'RECHAZADO': 'red',
        }
        iconos = {
            'PENDIENTE': '⏳',
            'APROBADO': '✅',
            'RECHAZADO': '❌',
        }
        color = colors.get(obj.estado, 'gray')
        icono = iconos.get(obj.estado, '❓')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            icono,
            obj.get_estado_display()
        )
    estado_coloreado.short_description = 'Estado'
    estado_coloreado.admin_order_field = 'estado'
    
    def fechaAsignacion_corta(self, obj):
        """Fecha en formato corto"""
        return obj.fechaAsignacion.strftime('%d/%m/%Y %H:%M') if obj.fechaAsignacion else '-'
    fechaAsignacion_corta.short_description = 'Asignación'
    fechaAsignacion_corta.admin_order_field = 'fechaAsignacion'
    
    def get_queryset(self, request):
        """Optimizar consultas incluyendo las relaciones necesarias"""
        return super().get_queryset(request).select_related(
            'solicitud',
            'solicitud__actividad',
            'solicitud__tarea',
            'usuarioValidador',
            'usuarioRedactor'
        )
    
    actions = ['marcar_como_aprobado', 'marcar_como_rechazado']
    
    def marcar_como_aprobado(self, request, queryset):
        """Action para aprobar validaciones de viaje"""
        contador = 0
        for v in queryset:
            v.estado = 'APROBADO'
            v.save()
            contador += 1
        self.message_user(request, f"✈️ {contador} validaciones de viaje marcadas como APROBADAS")
    marcar_como_aprobado.short_description = "✅ Marcar como APROBADO"
    
    def marcar_como_rechazado(self, request, queryset):
        """Action para rechazar validaciones de viaje"""
        contador = 0
        for v in queryset:
            v.estado = 'RECHAZADO'
            v.save()
            contador += 1
        self.message_user(request, f"✈️ {contador} validaciones de viaje marcadas como RECHAZADAS")
    marcar_como_rechazado.short_description = "❌ Marcar como RECHAZADO"

# -------------------------------------------------------------------
# ADMIN PARA VALIDACIONES DE SOLICITUD DE PAGO DIRECTO
# -------------------------------------------------------------------
@admin.register(ValidacionSolicitudPagoDirecto)
class ValidacionSolicitudPagoDirectoAdmin(admin.ModelAdmin):
    """
    Admin para validaciones de Solicitudes de Pago Directo
    """
    list_display = [
        'id',
        'codigoSeguimiento',
        'solicitud_link',
        'usuarioValidador',
        'estado_coloreado',
        'tipo_solicitud_coloreado',
        'versionDocumento',
        'fechaAsignacion_corta'
    ]
    
    list_filter = [
        'estado',
        'versionDocumento',
        'fechaAsignacion',
        'solicitud__actividad',  # Para filtrar por actividad
    ]
    
    search_fields = [
        'codigoSeguimiento',
        'solicitud__numeroFormulario',
        'usuarioValidador__username',
        'usuarioValidador__first_name',
        'usuarioValidador__last_name',
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
        """Link a la solicitud de pago directo en admin"""
        url = f"/admin/spme_viajes/solicitudpagodirecto/{obj.solicitud.id}/change/"
        return format_html('<a href="{}">💳 {}</a>', url, obj.codigo_solicitud)
    solicitud_link.short_description = 'Solicitud de Pago Directo'
    solicitud_link.admin_order_field = 'solicitud__numeroFormulario'
    
    def solicitud_detalle(self, obj):
        """Muestra detalles de la solicitud de pago directo"""
        if obj.solicitud:
            detalles = []
            
            # Código de formulario
            detalles.append(
                f'<strong>Formulario:</strong> {obj.codigo_solicitud}'
            )
            
            # Tipo de solicitud
            tipo = obj.tipo_solicitud
            tipo_colores = {
                'ACTIVIDAD': '#3498db',
                'TAREA': '#9b59b6',
                'GENERAL': '#95a5a6'
            }
            color_tipo = tipo_colores.get(tipo, '#95a5a6')
            detalles.append(
                f'<strong>Tipo:</strong> <span style="color: {color_tipo}; font-weight: bold;">{tipo}</span>'
            )
            
            # Monto
            detalles.append(
                f'<strong>Monto:</strong> {obj.monto_solicitud:,.2f}' if obj.monto_solicitud else '<strong>Monto:</strong> -'
            )
            
            # Actividad o Tarea relacionada
            if obj.solicitud.actividad:
                detalles.append(
                    f'<strong>Actividad:</strong> {obj.solicitud.actividad}'
                )
            if obj.solicitud.tarea:
                detalles.append(
                    f'<strong>Tarea:</strong> {obj.solicitud.tarea}'
                )
            
            # Solicitante
            if hasattr(obj.solicitud, 'usuario') and obj.solicitud.usuario:
                detalles.append(
                    f'<strong>Solicitante:</strong> {obj.solicitud.usuario.get_full_name() or obj.solicitud.usuario.username}'
                )
            
            # Beneficiario si existe
            if hasattr(obj.solicitud, 'beneficiario') and obj.solicitud.beneficiario:
                detalles.append(
                    f'<strong>Beneficiario:</strong> {obj.solicitud.beneficiario}'
                )
            
            # Concepto si existe
            if hasattr(obj.solicitud, 'concepto') and obj.solicitud.concepto:
                detalles.append(
                    f'<strong>Concepto:</strong> {obj.solicitud.concepto}'
                )
            
            # Fecha de la solicitud si existe
            if hasattr(obj.solicitud, 'fechaSolicitud') and obj.solicitud.fechaSolicitud:
                detalles.append(
                    f'<strong>Fecha Solicitud:</strong> {obj.solicitud.fechaSolicitud.strftime("%d/%m/%Y")}'
                )
            
            return format_html('<br>'.join(detalles))
        return '-'
    solicitud_detalle.short_description = 'Detalles de la Solicitud'
    
    def tipo_solicitud_coloreado(self, obj):
        """Muestra el tipo de solicitud con colores"""
        tipo = obj.tipo_solicitud
        colores = {
            'ACTIVIDAD': '#3498db',  # Azul
            'TAREA': '#9b59b6',      # Púrpura
            'GENERAL': '#95a5a6'     # Gris
        }
        iconos = {
            'ACTIVIDAD': '📋',
            'TAREA': '✅',
            'GENERAL': '📄'
        }
        color = colores.get(tipo, '#95a5a6')
        icono = iconos.get(tipo, '📄')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            icono,
            tipo
        )
    tipo_solicitud_coloreado.short_description = 'Tipo'
    
    def estado_coloreado(self, obj):
        """Muestra el estado con colores"""
        colors = {
            'PENDIENTE': 'orange',
            'APROBADO': 'green',
            'RECHAZADO': 'red',
        }
        iconos = {
            'PENDIENTE': '⏳',
            'APROBADO': '✅',
            'RECHAZADO': '❌',
        }
        color = colors.get(obj.estado, 'gray')
        icono = iconos.get(obj.estado, '❓')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            icono,
            obj.get_estado_display()
        )
    estado_coloreado.short_description = 'Estado'
    estado_coloreado.admin_order_field = 'estado'
    
    def fechaAsignacion_corta(self, obj):
        """Fecha en formato corto"""
        return obj.fechaAsignacion.strftime('%d/%m/%Y %H:%M') if obj.fechaAsignacion else '-'
    fechaAsignacion_corta.short_description = 'Asignación'
    fechaAsignacion_corta.admin_order_field = 'fechaAsignacion'
    
    def get_queryset(self, request):
        """Optimizar consultas incluyendo las relaciones necesarias"""
        return super().get_queryset(request).select_related(
            'solicitud',
            'solicitud__actividad',
            'solicitud__tarea',
            'usuarioValidador',
            'usuarioRedactor'
        )
    
    actions = ['marcar_como_aprobado', 'marcar_como_rechazado']
    
    def marcar_como_aprobado(self, request, queryset):
        """Action para aprobar validaciones de pago directo"""
        contador = 0
        for v in queryset:
            v.estado = 'APROBADO'
            v.save()
            contador += 1
        self.message_user(request, f"💳 {contador} validaciones de pago directo marcadas como APROBADAS")
    marcar_como_aprobado.short_description = "✅ Marcar como APROBADO"
    
    def marcar_como_rechazado(self, request, queryset):
        """Action para rechazar validaciones de pago directo"""
        contador = 0
        for v in queryset:
            v.estado = 'RECHAZADO'
            v.save()
            contador += 1
        self.message_user(request, f"💳 {contador} validaciones de pago directo marcadas como RECHAZADAS")
    marcar_como_rechazado.short_description = "❌ Marcar como RECHAZADO"


# -------------------------------------------------------------------
# ADMIN PARA VALIDACIONES DE SOLICITUD DE REEMBOLSO
# -------------------------------------------------------------------
@admin.register(ValidacionSolicitudReembolso)
class ValidacionSolicitudReembolsoAdmin(admin.ModelAdmin):
    """
    Admin para validaciones de Solicitudes de Reembolso
    """
    list_display = [
        'id',
        'codigoSeguimiento',
        'solicitud_link',
        'usuarioValidador',
        'estado_coloreado',
        'tipo_solicitud_coloreado',
        'versionDocumento',
        'fechaAsignacion_corta'
    ]
    
    list_filter = [
        'estado',
        'versionDocumento',
        'fechaAsignacion',
        'solicitud__actividad',  # Para filtrar por actividad
    ]
    
    search_fields = [
        'codigoSeguimiento',
        'solicitud__numeroFormulario',
        'usuarioValidador__username',
        'usuarioValidador__first_name',
        'usuarioValidador__last_name',
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
        """Link a la solicitud de reembolso en admin"""
        url = f"/admin/spme_viajes/solicitudreembolso/{obj.solicitud.id}/change/"
        return format_html('<a href="{}">♻️ {}</a>', url, obj.codigo_solicitud)
    solicitud_link.short_description = 'Solicitud de Reembolso'
    solicitud_link.admin_order_field = 'solicitud__numeroFormulario'
    
    def solicitud_detalle(self, obj):
        """Muestra detalles de la solicitud de reembolso"""
        if obj.solicitud:
            detalles = []
            
            # Código de formulario
            detalles.append(
                f'<strong>Formulario:</strong> {obj.codigo_solicitud}'
            )
            
            # Tipo de solicitud
            tipo = obj.tipo_solicitud
            tipo_colores = {
                'ACTIVIDAD': '#3498db',
                'TAREA': '#9b59b6',
                'GENERAL': '#95a5a6'
            }
            color_tipo = tipo_colores.get(tipo, '#95a5a6')
            detalles.append(
                f'<strong>Tipo:</strong> <span style="color: {color_tipo}; font-weight: bold;">{tipo}</span>'
            )
            
            # Monto
            if obj.monto_solicitud:
                detalles.append(
                    f'<strong>Monto:</strong> {obj.monto_solicitud:,.2f}'
                )
            else:
                detalles.append('<strong>Monto:</strong> -')
            
            # Actividad o Tarea relacionada
            if obj.solicitud.actividad:
                detalles.append(
                    f'<strong>Actividad:</strong> {obj.solicitud.actividad}'
                )
            if obj.solicitud.tarea:
                detalles.append(
                    f'<strong>Tarea:</strong> {obj.solicitud.tarea}'
                )
            
            # Solicitante
            if hasattr(obj.solicitud, 'usuario') and obj.solicitud.usuario:
                detalles.append(
                    f'<strong>Solicitante:</strong> {obj.solicitud.usuario.get_full_name() or obj.solicitud.usuario.username}'
                )
            
            # Beneficiario si existe
            if hasattr(obj.solicitud, 'beneficiario') and obj.solicitud.beneficiario:
                detalles.append(
                    f'<strong>Beneficiario:</strong> {obj.solicitud.beneficiario}'
                )
            
            # Concepto si existe
            if hasattr(obj.solicitud, 'concepto') and obj.solicitud.concepto:
                detalles.append(
                    f'<strong>Concepto:</strong> {obj.solicitud.concepto}'
                )
            
            # Fecha de la solicitud si existe
            if hasattr(obj.solicitud, 'fechaSolicitud') and obj.solicitud.fechaSolicitud:
                detalles.append(
                    f'<strong>Fecha Solicitud:</strong> {obj.solicitud.fechaSolicitud.strftime("%d/%m/%Y")}'
                )
            
            return format_html('<br>'.join(detalles))
        return '-'
    solicitud_detalle.short_description = 'Detalles de la Solicitud'
    
    def tipo_solicitud_coloreado(self, obj):
        """Muestra el tipo de solicitud con colores"""
        tipo = obj.tipo_solicitud
        colores = {
            'ACTIVIDAD': '#3498db',  # Azul
            'TAREA': '#9b59b6',      # Púrpura
            'GENERAL': '#95a5a6'     # Gris
        }
        iconos = {
            'ACTIVIDAD': '📋',
            'TAREA': '✅',
            'GENERAL': '📄'
        }
        color = colores.get(tipo, '#95a5a6')
        icono = iconos.get(tipo, '📄')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            icono,
            tipo
        )
    tipo_solicitud_coloreado.short_description = 'Tipo'
    
    def estado_coloreado(self, obj):
        """Muestra el estado con colores"""
        colors = {
            'PENDIENTE': 'orange',
            'APROBADO': 'green',
            'RECHAZADO': 'red',
        }
        iconos = {
            'PENDIENTE': '⏳',
            'APROBADO': '✅',
            'RECHAZADO': '❌',
        }
        color = colors.get(obj.estado, 'gray')
        icono = iconos.get(obj.estado, '❓')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            icono,
            obj.get_estado_display()
        )
    estado_coloreado.short_description = 'Estado'
    estado_coloreado.admin_order_field = 'estado'
    
    def fechaAsignacion_corta(self, obj):
        """Fecha en formato corto"""
        return obj.fechaAsignacion.strftime('%d/%m/%Y %H:%M') if obj.fechaAsignacion else '-'
    fechaAsignacion_corta.short_description = 'Asignación'
    fechaAsignacion_corta.admin_order_field = 'fechaAsignacion'
    
    def get_queryset(self, request):
        """Optimizar consultas incluyendo las relaciones necesarias"""
        return super().get_queryset(request).select_related(
            'solicitud',
            'solicitud__actividad',
            'solicitud__tarea',
            'usuarioValidador',
            'usuarioRedactor'
        )
    
    actions = ['marcar_como_aprobado', 'marcar_como_rechazado']
    
    def marcar_como_aprobado(self, request, queryset):
        """Action para aprobar validaciones de reembolso"""
        contador = 0
        for v in queryset:
            v.estado = 'APROBADO'
            v.save()
            contador += 1
        self.message_user(request, f"♻️ {contador} validaciones de reembolso marcadas como APROBADAS")
    marcar_como_aprobado.short_description = "✅ Marcar como APROBADO"
    
    def marcar_como_rechazado(self, request, queryset):
        """Action para rechazar validaciones de reembolso"""
        contador = 0
        for v in queryset:
            v.estado = 'RECHAZADO'
            v.save()
            contador += 1
        self.message_user(request, f"♻️ {contador} validaciones de reembolso marcadas como RECHAZADAS")
    marcar_como_rechazado.short_description = "❌ Marcar como RECHAZADO"


# -------------------------------------------------------------------
# ADMIN PARA VALIDACIONES DE RENDICIÓN DE CUENTAS
# -------------------------------------------------------------------
@admin.register(ValidacionRendicionCuentas)
class ValidacionRendicionCuentasAdmin(admin.ModelAdmin):
    """
    Admin para validaciones de Rendiciones de Cuentas
    """
    list_display = [
        'id',
        'codigoSeguimiento',
        'rendicion_link',
        'usuarioValidador',
        'estado_coloreado',
        'tipo_rendicion_coloreado',
        'versionDocumento',
        'fechaAsignacion_corta'
    ]
    
    list_filter = [
        'estado',
        'versionDocumento',
        'fechaAsignacion',
        'rendicion__actividad',  # Para filtrar por actividad
    ]
    
    search_fields = [
        'codigoSeguimiento',
        'rendicion__numeroFormulario',
        'usuarioValidador__username',
        'usuarioValidador__first_name',
        'usuarioValidador__last_name',
        'comentarios'
    ]
    
    raw_id_fields = ['rendicion', 'usuarioValidador', 'usuarioRedactor']
    
    readonly_fields = [
        'codigoSeguimiento',
        'fechaAsignacion',
        'fechaResolucion',
        'rendicion_detalle'
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
        ('Rendición Relacionada', {
            'fields': (
                'rendicion',
                'rendicion_detalle'
            )
        }),
        ('Fechas', {
            'fields': (
                ('fechaAsignacion', 'fechaResolucion'),
            )
        }),
    )
    
    def rendicion_link(self, obj):
        """Link a la rendición de cuentas en admin"""
        url = f"/admin/spme_viajes/rendicioncuentas/{obj.rendicion.id}/change/"
        return format_html('<a href="{}">📊 {}</a>', url, obj.codigo_rendicion)
    rendicion_link.short_description = 'Rendición de Cuentas'
    rendicion_link.admin_order_field = 'rendicion__numeroFormulario'
    
    def rendicion_detalle(self, obj):
        """Muestra detalles de la rendición de cuentas"""
        if obj.rendicion:
            detalles = []
            
            # Código de formulario
            detalles.append(
                f'<strong>Formulario:</strong> {obj.codigo_rendicion}'
            )
            
            # Tipo de rendición
            tipo = obj.tipo_rendicion
            tipo_colores = {
                'ACTIVIDAD': '#3498db',
                'TAREA': '#9b59b6',
                'GENERAL': '#95a5a6'
            }
            color_tipo = tipo_colores.get(tipo, '#95a5a6')
            detalles.append(
                f'<strong>Tipo:</strong> <span style="color: {color_tipo}; font-weight: bold;">{tipo}</span>'
            )
            
            # Monto asignado
            if obj.monto_rendicion:
                detalles.append(
                    f'<strong>Monto Asignado:</strong> {obj.monto_rendicion:,.2f}'
                )
            else:
                detalles.append('<strong>Monto Asignado:</strong> -')
            
            # Saldo si existe
            if obj.saldo_rendicion is not None:
                detalles.append(
                    f'<strong>Saldo:</strong> {obj.saldo_rendicion:,.2f}'
                )
            
            # Actividad o Tarea relacionada
            if obj.rendicion.actividad:
                detalles.append(
                    f'<strong>Actividad:</strong> {obj.rendicion.actividad}'
                )
            if obj.rendicion.tarea:
                detalles.append(
                    f'<strong>Tarea:</strong> {obj.rendicion.tarea}'
                )
            
            # Solicitante
            if hasattr(obj.rendicion, 'usuario') and obj.rendicion.usuario:
                detalles.append(
                    f'<strong>Solicitante:</strong> {obj.rendicion.usuario.get_full_name() or obj.rendicion.usuario.username}'
                )
            
            # Fecha de la rendición si existe
            if hasattr(obj.rendicion, 'fechaRendicion') and obj.rendicion.fechaRendicion:
                detalles.append(
                    f'<strong>Fecha Rendición:</strong> {obj.rendicion.fechaRendicion.strftime("%d/%m/%Y")}'
                )
            
            return format_html('<br>'.join(detalles))
        return '-'
    rendicion_detalle.short_description = 'Detalles de la Rendición'
    
    def tipo_rendicion_coloreado(self, obj):
        """Muestra el tipo de rendición con colores"""
        tipo = obj.tipo_rendicion
        colores = {
            'ACTIVIDAD': '#3498db',  # Azul
            'TAREA': '#9b59b6',      # Púrpura
            'GENERAL': '#95a5a6'     # Gris
        }
        iconos = {
            'ACTIVIDAD': '📋',
            'TAREA': '✅',
            'GENERAL': '📄'
        }
        color = colores.get(tipo, '#95a5a6')
        icono = iconos.get(tipo, '📄')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            icono,
            tipo
        )
    tipo_rendicion_coloreado.short_description = 'Tipo'
    
    def estado_coloreado(self, obj):
        """Muestra el estado con colores"""
        colors = {
            'PENDIENTE': 'orange',
            'APROBADO': 'green',
            'RECHAZADO': 'red',
        }
        iconos = {
            'PENDIENTE': '⏳',
            'APROBADO': '✅',
            'RECHAZADO': '❌',
        }
        color = colors.get(obj.estado, 'gray')
        icono = iconos.get(obj.estado, '❓')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            icono,
            obj.get_estado_display()
        )
    estado_coloreado.short_description = 'Estado'
    estado_coloreado.admin_order_field = 'estado'
    
    def fechaAsignacion_corta(self, obj):
        """Fecha en formato corto"""
        return obj.fechaAsignacion.strftime('%d/%m/%Y %H:%M') if obj.fechaAsignacion else '-'
    fechaAsignacion_corta.short_description = 'Asignación'
    fechaAsignacion_corta.admin_order_field = 'fechaAsignacion'
    
    def get_queryset(self, request):
        """Optimizar consultas incluyendo las relaciones necesarias"""
        return super().get_queryset(request).select_related(
            'rendicion',
            'rendicion__actividad',
            'rendicion__tarea',
            'usuarioValidador',
            'usuarioRedactor'
        )
    
    actions = ['marcar_como_aprobado', 'marcar_como_rechazado']
    
    def marcar_como_aprobado(self, request, queryset):
        """Action para aprobar validaciones de rendición"""
        contador = 0
        for v in queryset:
            v.estado = 'APROBADO'
            v.save()
            contador += 1
        self.message_user(request, f"📊 {contador} validaciones de rendición marcadas como APROBADAS")
    marcar_como_aprobado.short_description = "✅ Marcar como APROBADO"
    
    def marcar_como_rechazado(self, request, queryset):
        """Action para rechazar validaciones de rendición"""
        contador = 0
        for v in queryset:
            v.estado = 'RECHAZADO'
            v.save()
            contador += 1
        self.message_user(request, f"📊 {contador} validaciones de rendición marcadas como RECHAZADAS")
    marcar_como_rechazado.short_description = "❌ Marcar como RECHAZADO"

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
        'comentario',
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