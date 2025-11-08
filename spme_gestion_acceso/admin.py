from django.contrib import admin
from .models import UserInstanciaGestora, PermisoProyectoEspecifico

@admin.register(UserInstanciaGestora)
class UserInstanciaGestoraAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'instancia_gestora', 'nivel_acceso_display', 'activo', 'fecha_asignacion']
    list_filter = ['activo', 'nivel_acceso', 'instancia_gestora']
    search_fields = ['usuario__username', 'usuario__nombre', 'instancia_gestora__instancia']
    
    def nivel_acceso_display(self, obj):
        from .services.permission_service import PermissionService
        return PermissionService().obtener_nombre_nivel_acceso(obj.nivel_acceso)
    nivel_acceso_display.short_description = 'Nivel de Acceso'

@admin.register(PermisoProyectoEspecifico)
class PermisoProyectoEspecificoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'proyecto', 'tipo_acceso_display', 'activo', 'fecha_expiracion']
    list_filter = ['activo', 'tipo_acceso', 'proyecto']
    search_fields = ['usuario__username', 'usuario__nombre', 'proyecto__codigo', 'proyecto__titulo']
    
    def tipo_acceso_display(self, obj):
        from .services.permission_service import PermissionService
        return PermissionService().obtener_nombre_nivel_acceso(obj.tipo_acceso)
    tipo_acceso_display.short_description = 'Tipo de Acceso'