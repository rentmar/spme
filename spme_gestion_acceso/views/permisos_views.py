from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.db import models
from ..services import PermissionService
from spme_estructuracion_proyecto.models import Proyecto

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def obtener_permisos_usuario(request):
    """Endpoint para obtener todos los permisos del usuario (cache en frontend)"""
    permission_service = PermissionService()
    
    instancias_gestoras = permission_service.obtener_instancias_gestoras_usuario(request.user)
    
    proyectos_accesibles = []
    proyectos = permission_service.obtener_proyectos_accesibles(request.user)
    
    for proyecto in proyectos:
        nivel = permission_service.obtener_nivel_acceso_proyecto(request.user, proyecto)
        proyectos_accesibles.append({
            'id': proyecto.id,
            'codigo': proyecto.codigo,
            'titulo': proyecto.titulo,
            'nivel_acceso': nivel,
            'nivel_acceso_display': permission_service.obtener_nombre_nivel_acceso(nivel)
        })
    
    return Response({
        'user': {
            'id': request.user.id,
            'username': request.user.username,
            'nombre_completo': request.user.get_full_name(),
            'is_superuser': request.user.is_superuser
        },
        'instancias_gestoras': [
            {
                'id': ui.instancia_gestora.id,
                'codigo': ui.instancia_gestora.codigo,
                'instancia': ui.instancia_gestora.instancia,
                'nivel_acceso': ui.nivel_acceso,
                'nivel_acceso_display': permission_service.obtener_nombre_nivel_acceso(ui.nivel_acceso)
            }
            for ui in instancias_gestoras
        ],
        'proyectos_accesibles': proyectos_accesibles,
        'niveles_acceso': {
            'sin_acceso': permission_service.SIN_ACCESO,
            'lectura': permission_service.LECTURA,
            'edicion': permission_service.EDICION,
            'administracion': permission_service.ADMINISTRACION
        }
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def verificar_acceso_proyecto(request, proyecto_id):
    """Verificación en tiempo real de acceso a proyecto específico"""
    try:
        # Usar prefetch_related para ManyToMany
        proyecto = Proyecto.objects.prefetch_related('instancia_gestora').get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return Response(
            {'error': 'Proyecto no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    permission_service = PermissionService()
    acceso, nivel = permission_service.tiene_acceso_proyecto(request.user, proyecto)
    
    return Response({
        'proyecto': {
            'id': proyecto.id,
            'codigo': proyecto.codigo,
            'titulo': proyecto.titulo
        },
        'acceso': acceso,
        'nivel_acceso': nivel,
        'nivel_acceso_display': permission_service.obtener_nombre_nivel_acceso(nivel),
        'puede_ver': permission_service.puede_ver_proyecto(request.user, proyecto),
        'puede_editar': permission_service.puede_editar_proyecto(request.user, proyecto),
        'puede_administrar': permission_service.puede_administrar_proyecto(request.user, proyecto)
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def lista_proyectos_accesibles(request):
    """Obtener lista paginada de proyectos accesibles"""
    permission_service = PermissionService()
    proyectos = permission_service.obtener_proyectos_accesibles(request.user)
    
    # Filtros opcionales
    estado = request.GET.get('estado')
    if estado:
        proyectos = proyectos.filter(estado=estado)
    
    # Búsqueda
    search = request.GET.get('search')
    if search:
        proyectos = proyectos.filter(
            models.Q(codigo__icontains=search) |
            models.Q(titulo__icontains=search)
        )
    
    # Paginación
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size
    
    proyectos_paginados = proyectos[start:end]
    
    proyectos_data = []
    for proyecto in proyectos_paginados:
        nivel = permission_service.obtener_nivel_acceso_proyecto(request.user, proyecto)
        proyectos_data.append({
            'id': proyecto.id,
            'codigo': proyecto.codigo,
            'titulo': proyecto.titulo,
            'estado': proyecto.estado,
            'fecha_creacion': proyecto.fecha_creacion,
            'nivel_acceso': nivel,
            'nivel_acceso_display': permission_service.obtener_nombre_nivel_acceso(nivel)
        })
    
    return Response({
        'proyectos': proyectos_data,
        'paginacion': {
            'pagina_actual': page,
            'tamano_pagina': page_size,
            'total_proyectos': proyectos.count(),
            'total_paginas': (proyectos.count() + page_size - 1) // page_size
        },
        'filtros': {
            'estado': estado,
            'search': search
        }
    })