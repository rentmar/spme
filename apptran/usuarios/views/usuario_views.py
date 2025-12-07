
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q

from spme_autenticacion.models import Usuario
from ..serializers.usuario_serializer import UsuarioListSerializer

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def listar_usuarios(request):
    """
    Lista todos los usuarios activos en formato simplificado
    EXCLUYE a los superusuarios (is_superuser=True)
    
    GET /api/usuarios/
    
    Query Params:
        q: Término de búsqueda (opcional, busca en nombre, username o cargo)
        limit: Límite de resultados (default: 50, max: 100)
        offset: Offset para paginación (default: 0)
        excluir_actual: Si es true, excluye al usuario actual (default: false)
        incluir_superusuarios: Si es true, incluye superusuarios (default: false)
    
    Returns:
        {
            "success": true,
            "data": [
                {
                    "id": 2,
                    "nombre_completo": "Juan Pérez",
                    "username": "jperez",
                    "email": "jperez@empresa.com",
                    "cargo": "Desarrollador"
                },
                ...
            ],
            "total": 25,
            "paginacion": {
                "limit": 50,
                "offset": 0,
                "has_more": true
            }
        }
    """
    try:
        usuario_actual = request.user
        
        # Obtener parámetros de filtro
        query = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 50))
        offset = int(request.GET.get('offset', 0))
        excluir_actual = request.GET.get('excluir_actual', 'false').lower() == 'true'
        incluir_superusuarios = request.GET.get('incluir_superusuarios', 'false').lower() == 'true'
        
        # Validar límite
        if limit > 100:
            limit = 100
        
        # Construir queryset base - EXCLUIR SUPERUSUARIOS por defecto
        usuarios = Usuario.objects.filter(is_active=True)
        
        # Solo incluir superusuarios si se solicita explícitamente
        if not incluir_superusuarios:
            usuarios = usuarios.filter(is_superuser=False)
        
        # Excluir usuario actual si se solicita
        if excluir_actual:
            usuarios = usuarios.exclude(id=usuario_actual.id)
        
        # Aplicar búsqueda si hay término
        if query:
            usuarios = usuarios.filter(
                Q(nombre__icontains=query) |
                Q(paterno__icontains=query) |
                Q(materno__icontains=query) |
                Q(username__icontains=query) |
                Q(cargo__icontains=query)
            )
        
        # Ordenar por nombre completo
        usuarios = usuarios.order_by('nombre', 'paterno', 'materno')
        
        # Obtener total (antes de paginar)
        total = usuarios.count()
        
        # Aplicar paginación
        usuarios = usuarios[offset:offset + limit]
        
        # Serializar datos
        serializer = UsuarioListSerializer(usuarios, many=True)
        
        # Determinar si hay más resultados
        has_more = (offset + limit) < total
        
        return Response({
            'success': True,
            'data': serializer.data,
            'total': total,
            'paginacion': {
                'limit': limit,
                'offset': offset,
                'has_more': has_more
            },
            'filtros_aplicados': {
                'excluye_superusuarios': not incluir_superusuarios,
                'excluye_actual': excluir_actual,
                'tiene_busqueda': bool(query)
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def buscar_usuarios_autocomplete(request):
    """
    Búsqueda rápida de usuarios para autocomplete
    EXCLUYE a los superusuarios por defecto
    
    GET /api/usuarios/buscar/
    
    Query Params:
        q: Término de búsqueda (requerido, min: 2 caracteres)
        limit: Límite de resultados (default: 10, max: 20)
        incluir_superusuarios: Si es true, incluye superusuarios (default: false)
    
    Returns:
        {
            "success": true,
            "data": [
                {
                    "id": 2,
                    "nombre_completo": "Juan Pérez",
                    "username": "jperez",
                    "email": "jperez@empresa.com",
                    "cargo": "Desarrollador"
                },
                ...
            ]
        }
    """
    try:
        query = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 10))
        incluir_superusuarios = request.GET.get('incluir_superusuarios', 'false').lower() == 'true'
        
        if not query or len(query) < 2:
            return Response({
                'success': True,
                'data': [],
                'message': 'Ingrese al menos 2 caracteres para buscar'
            }, status=status.HTTP_200_OK)
        
        # Validar límite
        if limit > 20:
            limit = 20
        
        # Buscar usuarios - EXCLUIR SUPERUSUARIOS por defecto
        usuarios = Usuario.objects.filter(is_active=True)
        
        # Solo incluir superusuarios si se solicita explícitamente
        if not incluir_superusuarios:
            usuarios = usuarios.filter(is_superuser=False)
        
        # Aplicar búsqueda
        usuarios = usuarios.filter(
            Q(nombre__icontains=query) |
            Q(paterno__icontains=query) |
            Q(materno__icontains=query) |
            Q(username__icontains=query) |
            Q(cargo__icontains=query)
        ).order_by('nombre', 'paterno', 'materno')[:limit]
        
        # Serializar datos
        serializer = UsuarioListSerializer(usuarios, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'total': len(serializer.data),
            'query': query,
            'filtros_aplicados': {
                'excluye_superusuarios': not incluir_superusuarios
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def obtener_usuario_actual(request):
    """
    Obtiene la información del usuario actualmente autenticado
    
    GET /api/usuarios/yo/
    
    Returns:
        {
            "success": true,
            "data": {
                "id": 1,
                "nombre_completo": "Admin Sistema",
                "username": "admin",
                "email": "admin@empresa.com",
                "cargo": "Administrador",
                "es_superusuario": true,
                "es_staff": true
            }
        }
    """
    try:
        usuario = request.user
        
        datos = {
            'id': usuario.id,
            'nombre_completo': usuario.get_full_name(),
            'username': usuario.username,
            'email': f"{usuario.username}@empresa.com",
            'cargo': usuario.cargo or 'Sin cargo asignado',
            'es_superusuario': usuario.is_superuser,
            'es_staff': usuario.is_staff,
            'permisos': usuario.permisos or 'Sin permisos específicos'
        }
        
        return Response({
            'success': True,
            'data': datos
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def listar_usuarios_publico(request):
    """
    Lista usuarios activos (endpoint público para formularios)
    EXCLUYE a los superusuarios
    
    GET /api/usuarios/public/
    
    Query Params:
        incluir_superusuarios: Si es true, incluye superusuarios (default: false)
    
    Returns:
        {
            "success": true,
            "data": [
                {
                    "id": 2,
                    "nombre_completo": "Juan Pérez",
                    "username": "jperez",
                    "email": "jperez@empresa.com",
                    "cargo": "Desarrollador"
                },
                ...
            ],
            "total": 25
        }
    """
    try:
        incluir_superusuarios = request.GET.get('incluir_superusuarios', 'false').lower() == 'true'
        
        # Base queryset
        usuarios = Usuario.objects.filter(is_active=True)
        
        # Solo incluir superusuarios si se solicita explícitamente
        if not incluir_superusuarios:
            usuarios = usuarios.filter(is_superuser=False)
        
        # Solo campos básicos
        datos = []
        for usuario in usuarios.order_by('nombre', 'paterno', 'materno'):
            datos.append({
                'id': usuario.id,
                'nombre_completo': usuario.get_full_name(),
                'username': usuario.username,
                'email': f"{usuario.username}@empresa.com",
                'cargo': usuario.cargo or 'Sin cargo asignado',
                'es_superusuario': usuario.is_superuser  # Para información
            })
        
        return Response({
            'success': True,
            'data': datos,
            'total': len(datos),
            'filtros_aplicados': {
                'excluye_superusuarios': not incluir_superusuarios
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)