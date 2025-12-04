from django.contrib import admin
from .models import MensajeUsuario, TipoMensaje, EstadoMensaje

@admin.register(MensajeUsuario)
class MensajeUsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'asunto', 'destinatario', 'tipo', 'estado', 'prioridad', 'fecha_envio')
    list_filter = ('tipo', 'estado', 'prioridad', 'fecha_envio', 'destinatario')
    search_fields = ('asunto', 'contenido', 'destinatario__username', 'remitente__username')
    readonly_fields = ('message_id', 'fecha_envio', 'fecha_leido', 'fecha_actualizacion')
    fieldsets = (
        ('Información Básica', {
            'fields': ('destinatario', 'remitente', 'asunto', 'contenido')
        }),
        ('Clasificación', {
            'fields': ('tipo', 'estado', 'prioridad', 'routing_key')
        }),
        ('Relaciones', {
            'fields': ('actividad_id', 'proyecto_id')
        }),
        ('Metadatos', {
            'fields': ('metadata', 'referencia_id', 'accion_url', 'accion_texto', 'icono')
        }),
        ('Sistema', {
            'fields': ('message_id', 'fecha_expiracion')
        }),
        ('Fechas', {
            'fields': ('fecha_envio', 'fecha_leido', 'fecha_actualizacion')
        }),
    )
    actions = ['marcar_como_leido', 'marcar_como_no_leido', 'archivar_mensajes']
    
    def marcar_como_leido(self, request, queryset):
        updated = queryset.filter(estado=EstadoMensaje.NO_LEIDO).update(estado=EstadoMensaje.LEIDO)
        self.message_user(request, f"{updated} mensajes marcados como leídos.")
    marcar_como_leido.short_description = "Marcar seleccionados como leídos"
    
    def marcar_como_no_leido(self, request, queryset):
        updated = queryset.filter(estado=EstadoMensaje.LEIDO).update(estado=EstadoMensaje.NO_LEIDO)
        self.message_user(request, f"{updated} mensajes marcados como no leídos.")
    marcar_como_no_leido.short_description = "Marcar seleccionados como no leídos"
    
    def archivar_mensajes(self, request, queryset):
        updated = queryset.update(estado=EstadoMensaje.ARCHIVADO)
        self.message_user(request, f"{updated} mensajes archivados.")
    archivar_mensajes.short_description = "Archivar mensajes seleccionados"

