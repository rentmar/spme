from rest_framework import permissions
from ..services.permission_service import PermissionService

class TieneAccesoProyecto(permissions.BasePermission):
    """Permiso base para ver proyectos"""
    def has_object_permission(self, request, view, obj):
        # Para objetos Proyecto
        if hasattr(obj, 'codigo'):  # Es un proyecto
            return PermissionService().puede_ver_proyecto(request.user, obj)
        return False

class PuedeEditarProyecto(permissions.BasePermission):
    """Permiso para editar proyectos (nivel EDICION o superior)"""
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'codigo'):  # Es un proyecto
            return PermissionService().puede_editar_proyecto(request.user, obj)
        return False

class PuedeAdministrarProyecto(permissions.BasePermission):
    """Permiso para administrar proyectos (nivel ADMINISTRACION)"""
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'codigo'):  # Es un proyecto
            return PermissionService().puede_administrar_proyecto(request.user, obj)
        return False

class PuedeAdministrarInstancia(permissions.BasePermission):
    """Permiso para administrar instancias gestoras"""
    def has_permission(self, request, view):
        return request.user.is_superuser
    
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser