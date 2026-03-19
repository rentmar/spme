# spme_monitor_estados/admin.py
# Propósito: Configuración de paneles de admin para los modelos con corrección de list_editable

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models.configuracion import ConfiguracionMonitoreo
from .models.cola_email import EmailEnCola

# ============================================================
# ADMIN PARA CONFIGURACION DE MONITOREO
# ============================================================

@admin.register(ConfiguracionMonitoreo)
class ConfiguracionMonitoreoAdmin(admin.ModelAdmin):
    """
    Panel de administración para ConfiguracionMonitoreo
    Permite gestionar la configuración de cada tipo de entidad
    """
    
    # Columnas a mostrar en la lista
    # NOTA: Se agrega 'activo' para cumplir con el requisito de list_editable
    list_display = [
        'id',
        'tipo_entidad_coloreado',
        'activo',  # Campo real necesario para list_editable
        'estado_badge',
        'prioridad_coloreada',
        'umbrales',
        'notificaciones',
        'actualizado_en'
    ]
    
    # Filtros laterales
    list_filter = ['activo', 'prioridad_notificacion', 'tipo_entidad']
    
    # Campos de búsqueda
    search_fields = ['tipo_entidad', 'descripcion']
    
    # Campos editables directamente en la lista
    # Este campo DEBE estar en list_display
    list_editable = ['activo']
    
    # Organización de campos en el formulario de edición
    fieldsets = (
        ('Entidad', {
            'fields': ('tipo_entidad', 'descripcion', 'activo')
        }),
        ('Prioridad de Email', {
            'fields': ('prioridad_notificacion',),
            'description': 'Determina el lote de envío (mayor prioridad = envío más rápido)'
        }),
        ('Umbrales de Retraso', {
            'fields': ('umbral_retraso_leve', 'umbral_retraso_critico'),
            'description': 'Días para considerar retraso'
        }),
        ('Notificaciones', {
            'fields': ('notificaciones_internas', 'notificaciones_email'),
            'description': 'Qué tipos de notificaciones enviar'
        }),
    )
    
    # ============================================================
    # MÉTODOS PARA PERSONALIZAR LA VISUALIZACIÓN
    # ============================================================
    
    def tipo_entidad_coloreado(self, obj):
        colores = {
            'actividad': '#28a745',
            'tarea': '#17a2b8',
            'actividad_pei': '#fd7e14',
            'tarea_pei': '#6f42c1',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colores.get(obj.tipo_entidad, 'black'),
            obj.get_tipo_entidad_display()
        )
    tipo_entidad_coloreado.short_description = 'Tipo'
    tipo_entidad_coloreado.admin_order_field = 'tipo_entidad'
    
    def estado_badge(self, obj):
        if obj.activo:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.8em;">ACTIVO</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.8em;">INACTIVO</span>'
        )
    estado_badge.short_description = 'Etiqueta'
    
    def prioridad_coloreada(self, obj):
        colores = {1: '#6c757d', 2: '#17a2b8', 3: '#fd7e14', 4: '#dc3545'}
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colores.get(obj.prioridad_notificacion, 'black'),
            obj.get_prioridad_notificacion_display()
        )
    prioridad_coloreada.short_description = 'Prioridad'
    
    def umbrales(self, obj):
        return f"L: {obj.umbral_retraso_leve}d | C: {obj.umbral_retraso_critico}d"
    umbrales.short_description = 'Umbrales'
    
    def notificaciones(self, obj):
        icons = []
        if obj.notificaciones_internas: icons.append('📨')
        if obj.notificaciones_email: icons.append('📧')
        return ' '.join(icons) if icons else '❌'
    notificaciones.short_description = 'Notif.'


# ============================================================
# ADMIN PARA COLA DE EMAILS
# ============================================================

@admin.register(EmailEnCola)
class EmailEnColaAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'asunto_resumido',
        'destinatario',
        'prioridad_coloreada',
        'estado_badge',
        'creado_en',
        'programado_para',
        'intentos'
    ]
    list_filter = ['estado', 'prioridad', 'tipo_entidad', 'creado_en']
    search_fields = ['destinatario', 'asunto']
    date_hierarchy = 'creado_en'
    actions = ['reintentar_emails', 'cancelar_emails']
    readonly_fields = ['creado_en', 'enviado_en', 'intentos', 'error']
    
    fieldsets = (
        ('Destinatario', {'fields': ('destinatario', 'copia', 'copia_oculta')}),
        ('Contenido', {'fields': ('asunto', 'cuerpo_html', 'cuerpo_texto'), 'classes': ('wide',)}),
        ('Control de Envío', {'fields': ('prioridad', 'estado', 'programado_para', 'creado_en', 'enviado_en')}),
        ('Origen y Errores', {'fields': ('tipo_entidad', 'entidad_id', 'evento', 'intentos', 'error'), 'classes': ('collapse',)}),
    )
    
    def asunto_resumido(self, obj):
        return obj.asunto[:50] + '...' if len(obj.asunto) > 50 else obj.asunto
    
    def prioridad_coloreada(self, obj):
        colores = {1: '#6c757d', 2: '#17a2b8', 3: '#fd7e14', 4: '#dc3545'}
        return format_html('<span style="color: {};">● {}</span>', colores.get(obj.prioridad, 'black'), obj.get_prioridad_display())
    
    def estado_badge(self, obj):
        colores = {'pendiente': '#ffc107', 'enviado': '#28a745', 'error': '#dc3545', 'cancelado': '#6c757d'}
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colores.get(obj.estado, '#6c757d'), obj.get_estado_display().upper()
        )

    def reintentar_emails(self, request, queryset):
        count = queryset.filter(estado='error').update(estado='pendiente', error='')
        self.message_user(request, f"✅ {count} emails marcados para reintentar")
    
    def cancelar_emails(self, request, queryset):
        count = queryset.filter(estado='pendiente').update(estado='cancelado')
        self.message_user(request, f"✅ {count} emails cancelados")