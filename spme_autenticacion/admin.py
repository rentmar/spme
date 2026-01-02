from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from .models import Usuario

# Formularios personalizados para validación
class UsuarioCreacionForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('username', 'nombre', 'paterno', 'materno', 'ci', 'correo', 'cargo', 'permisos')

class UsuarioCambioForm(UserChangeForm):
    class Meta:
        model = Usuario
        fields = '__all__'

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    form = UsuarioCambioForm
    add_form = UsuarioCreacionForm
    
    # Personalización de la lista principal
    list_display = (
        'username',
        'ci',
        'nombre_completo',
        'cargo',
        'correo',
        'permisos',
        'estado_visual',
        'is_staff_badge',
        'ultimo_login',
        'date_joined_short',
    )
    
    list_display_links = ('username', 'ci', 'nombre_completo')
    
    list_filter = (
        'permisos',
        'is_active',
        'is_staff',
        'cargo',
        'banco',
        'date_joined',
    )
    
    search_fields = (
        'username',
        'ci',
        'nombre',
        'paterno',
        'materno',
        'correo',
        'cargo',
        'banco',
        'numero_cuenta',
    )
    
    list_per_page = 25
    ordering = ('-date_joined',)
    
    # Campos de solo lectura
    readonly_fields = ('date_joined', 'last_login', 'informacion_resumen')
    
    # Organización en pestañas/tabs
    fieldsets = (
        (_('Información de Autenticación'), {
            'fields': ('username', 'password')
        }),
        (_('Información Personal'), {
            'fields': (
                ('nombre', 'paterno', 'materno'),
                'ci',
                'correo',
                'cargo'
            )
        }),
        (_('Información Bancaria'), {
            'fields': (
                'banco',
                ('numero_cuenta', 'tipo_cuenta'),
            ),
            'classes': ('collapse',),
            'description': _('Información opcional para pagos')
        }),
        (_('Permisos y Roles'), {
            'fields': (
                'permisos',
                'is_active',
                'is_staff',
                'groups',
                'user_permissions'
            ),
            'description': _('Control de acceso y permisos del usuario')
        }),
        (_('Información del Sistema'), {
            'fields': (
                'informacion_resumen',
                ('date_joined', 'last_login'),
            ),
            'classes': ('collapse',),
        }),
    )
    
    # Campos para creación de nuevo usuario (más simples)
    add_fieldsets = (
        (_('Credenciales'), {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2')
        }),
        (_('Información Obligatoria'), {
            'fields': (
                ('nombre', 'paterno', 'materno'),
                'ci',
                'correo',
                'cargo',
                'permisos'
            )
        }),
        (_('Información Adicional'), {
            'fields': (
                'banco',
                'numero_cuenta',
                'tipo_cuenta'
            ),
            'classes': ('collapse',),
        }),
        (_('Estado y Permisos'), {
            'fields': ('is_active', 'is_staff')
        }),
    )
    
    # Filtro horizontal para muchos-a-muchos
    filter_horizontal = ('groups', 'user_permissions',)
    
    # Métodos personalizados para visualización
    def nombre_completo(self, obj):
        return f"{obj.nombre} {obj.paterno} {obj.materno}".strip()
    nombre_completo.short_description = _('Nombre Completo')
    nombre_completo.admin_order_field = 'nombre'
    
    def estado_visual(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="display: inline-block; padding: 3px 8px; border-radius: 12px; '
                'background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb;">'
                '✅ Activo</span>'
            )
        return format_html(
            '<span style="display: inline-block; padding: 3px 8px; border-radius: 12px; '
            'background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb;">'
            '❌ Inactivo</span>'
        )
    estado_visual.short_description = _('Estado')
    
    def is_staff_badge(self, obj):
        if obj.is_staff:
            return format_html(
                '<span style="display: inline-block; padding: 3px 8px; border-radius: 12px; '
                'background-color: #cce5ff; color: #004085; border: 1px solid #b8daff;">'
                '👨‍💼 Staff</span>'
            )
        return format_html(
            '<span style="color: #6c757d; font-style: italic;">—</span>'
        )
    is_staff_badge.short_description = _('Staff')
    
    def ultimo_login(self, obj):
        if obj.last_login:
            from django.utils import timezone
            now = timezone.now()
            diff = now - obj.last_login
            
            if diff.days == 0:
                return _("Hoy")
            elif diff.days == 1:
                return _("Ayer")
            elif diff.days < 7:
                return _("Hace {} días").format(diff.days)
            elif diff.days < 30:
                return _("Hace {} semanas").format(diff.days // 7)
            else:
                return obj.last_login.strftime("%d/%m/%Y")
        return _("Nunca")
    ultimo_login.short_description = _('Último Login')
    
    def date_joined_short(self, obj):
        return obj.date_joined.strftime("%d/%m/%Y")
    date_joined_short.short_description = _('Registro')
    
    def informacion_resumen(self, obj):
        return format_html(
            '<div style="padding: 10px; background-color: #f8f9fa; border-radius: 5px; border: 1px solid #dee2e6;">'
            '<strong>Resumen:</strong><br>'
            f'• Usuario: {obj.username}<br>'
            f'• CI: {obj.ci}<br>'
            f'• Cargo: {obj.cargo}<br>'
            f'• Permisos: {obj.permisos}<br>'
            f'• Estado: {"Activo" if obj.is_active else "Inactivo"}<br>'
            f'• Staff: {"Sí" if obj.is_staff else "No"}<br>'
            f'• Registrado: {obj.date_joined.strftime("%d/%m/%Y %H:%M")}'
            '</div>'
        )
    informacion_resumen.short_description = _('Resumen del Usuario')
    
    # Acciones personalizadas
    actions = [
        'activar_usuarios',
        'desactivar_usuarios',
        'hacer_staff',
        'quitar_staff',
        'exportar_a_csv',
    ]
    
    def activar_usuarios(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            _('{count} usuario(s) activado(s) correctamente.').format(count=updated),
            level='SUCCESS'
        )
    activar_usuarios.short_description = _('✅ Activar usuarios seleccionados')
    
    def desactivar_usuarios(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            _('{count} usuario(s) desactivado(s) correctamente.').format(count=updated),
            level='WARNING'
        )
    desactivar_usuarios.short_description = _('⛔ Desactivar usuarios seleccionados')
    
    def hacer_staff(self, request, queryset):
        updated = queryset.update(is_staff=True)
        self.message_user(
            request,
            _('{count} usuario(s) ahora son staff.').format(count=updated),
            level='SUCCESS'
        )
    hacer_staff.short_description = _('👨‍💼 Convertir a staff')
    
    def quitar_staff(self, request, queryset):
        # Evitar desactivar staff si es el superusuario actual
        if request.user in queryset:
            self.message_user(
                request,
                _('No puedes quitarte a ti mismo el estado de staff.'),
                level='ERROR'
            )
            return
        
        updated = queryset.update(is_staff=False)
        self.message_user(
            request,
            _('{count} usuario(s) ya no son staff.').format(count=updated),
            level='WARNING'
        )
    quitar_staff.short_description = _('👤 Quitar staff')
    
    def exportar_a_csv(self, request, queryset):
        """Exporta los usuarios seleccionados a CSV"""
        import csv
        from django.http import HttpResponse
        import io
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="usuarios_exportados.csv"'
        
        # Usar io.StringIO para mejor manejo de encoding
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Escribir encabezados
        writer.writerow([
            'Username', 'CI', 'Nombre', 'Paterno', 'Materno',
            'Correo', 'Cargo', 'Banco', 'Número Cuenta', 'Tipo Cuenta',
            'Permisos', 'Estado', 'Staff', 'Fecha Registro'
        ])
        
        # Escribir datos
        for usuario in queryset:
            writer.writerow([
                usuario.username,
                usuario.ci or '',
                usuario.nombre or '',
                usuario.paterno or '',
                usuario.materno or '',
                usuario.correo or '',
                usuario.cargo or '',
                usuario.banco or '',
                usuario.numero_cuenta or '',
                usuario.tipo_cuenta or '',
                usuario.permisos or '',
                'Activo' if usuario.is_active else 'Inactivo',
                'Sí' if usuario.is_staff else 'No',
                usuario.date_joined.strftime("%Y-%m-%d %H:%M:%S")
            ])
        
        response.write(output.getvalue())
        return response
    exportar_a_csv.short_description = _('📊 Exportar seleccionados a CSV')
    
    # Mejoras de rendimiento
    def get_queryset(self, request):
        return super().get_queryset(request).only(
            'username', 'ci', 'nombre', 'paterno', 'materno',
            'correo', 'cargo', 'permisos', 'is_active', 'is_staff',
            'date_joined', 'last_login'
        )
    
    # Personalización de la vista de cambio
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = True
        extra_context['show_save_and_add_another'] = False
        return super().change_view(request, object_id, form_url, extra_context)
    
    # Log de acciones
    def save_model(self, request, obj, form, change):
        if change and 'password' in form.changed_data:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)
    
    # Personalización del template (opcional)
    class Media:
        css = {
            'all': ('admin/css/usuario_admin.css',)
        }
