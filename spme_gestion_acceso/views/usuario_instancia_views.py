#spme_gestion_acceso/views/usuario_instancia_views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from ..models import UserInstanciaGestora, PermisoProyectoEspecifico
from ..serializers import UserInstanciaGestoraSerializer, PermisoProyectoEspecificoSerializer
from ..permissions import PuedeAdministrarProyecto
from ..services import PermissionService

class UserInstanciaGestoraViewSet(viewsets.ModelViewSet):
    queryset = UserInstanciaGestora.objects.all()
    serializer_class = UserInstanciaGestoraSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return UserInstanciaGestora.objects.all()
        
        # Usuarios normales solo ven sus propias instancias
        return UserInstanciaGestora.objects.filter(usuario=self.request.user)
    
    @action(detail=False, methods=['get'])
    def mis_instancias(self, request):
        """Endpoint específico para obtener las instancias del usuario actual"""
        permission_service = PermissionService()
        instancias = permission_service.obtener_instancias_gestoras_usuario(request.user)
        
        serializer = self.get_serializer(instancias, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def por_instancia(self, request):
        """Endpoint para admin: obtener usuarios por instancia"""
        instancia_id = request.GET.get('instancia_id')
        if not instancia_id:
            return Response(
                {'error': 'Se requiere instancia_id'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        usuarios_instancia = UserInstanciaGestora.objects.filter(
            instancia_gestora_id=instancia_id, activo=True
        ).select_related('usuario', 'instancia_gestora')
        
        serializer = self.get_serializer(usuarios_instancia, many=True)
        return Response(serializer.data)

class PermisoProyectoEspecificoViewSet(viewsets.ModelViewSet):
    queryset = PermisoProyectoEspecifico.objects.all()
    serializer_class = PermisoProyectoEspecificoSerializer
    permission_classes = [permissions.IsAuthenticated, PuedeAdministrarProyecto]
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return PermisoProyectoEspecifico.objects.all()
        
        # Usuarios normales solo ven sus propios permisos específicos
        return PermisoProyectoEspecifico.objects.filter(usuario=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(asignado_por=self.request.user)
    
    @action(detail=False, methods=['get'])
    def mis_permisos_especificos(self, request):
        """Endpoint para obtener los permisos específicos del usuario"""
        permisos = PermisoProyectoEspecifico.objects.filter(
            usuario=request.user, activo=True
        ).select_related('proyecto', 'asignado_por')
        
        serializer = self.get_serializer(permisos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """Desactivar un permiso específico"""
        permiso = self.get_object()
        permiso.activo = False
        permiso.save()
        
        # Invalidar cache
        permission_service = PermissionService()
        permission_service.invalidar_cache_usuario(permiso.usuario_id)
        
        return Response({'status': 'Permiso desactivado'})