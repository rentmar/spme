#spme_gestion_acceso/views/permisos_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.db import models
from django.utils import timezone
from ..services import PermissionService
from spme_estructuracion_proyecto.models import Proyecto
from spme_autenticacion.models import Usuario  # Asegúrate de importar tu modelo de Usuario
from ..constants import NivelesAcceso

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
    
    #Obtener todos los datos del usuario
    user = request.user

    return Response({
        'user': {
            'id': request.user.id,
            'username': request.user.username,
            'nombre_completo': request.user.get_full_name(),
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': request.user.is_superuser,
            'date_joined': user.date_joined.isoformat() if user.date_joined else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,

            #Informacion personal
            'nombre': user.nombre,
            'paterno': user.paterno,
            'materno': user.materno,
            'nombre_completo': user.get_full_name(),
            'ci': user.ci,
            'cargo': user.cargo,
            'correo': user.correo,

            #Informacion bancaria
            'banco': user.banco,
            'numero_cuenta': user.numero_cuenta,
            'tipo_cuenta': user.tipo_cuenta,

            #Permisos y grupos
            'permisos': user.permisos,
            'groups': list(user.groups.values_list('name', flat=True)),
            'user_permissions': list(user.user_permissions.values_list('codename', flat=True))
        },
        'instancias_gestoras': [
            {
                'id': ui.instancia_gestora.id,
                'codigo': ui.instancia_gestora.codigo,
                'instancia': ui.instancia_gestora.instancia,
                'nivel_acceso': ui.nivel_acceso,
                'nivel_acceso_display': NivelesAcceso.NOMBRES.get(ui.nivel_acceso, 'Desconocido')  # ✅ Directo desde constantes
            }
            for ui in instancias_gestoras
        ],
        'proyectos_accesibles': proyectos_accesibles,
        'niveles_acceso': {
            'sin_acceso': NivelesAcceso.SIN_ACCESO,  # ✅ Directo desde constantes
            'lectura': NivelesAcceso.LECTURA,
            'edicion': NivelesAcceso.EDICION,
            'administracion': NivelesAcceso.ADMINISTRACION
        }
    })

def _get_client_ip(request):
    """Obtener la IP real del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

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
    
    # Información extendida del proyecto
    proyecto_data = {
        'id': proyecto.id,
        'codigo': proyecto.codigo,
        'titulo': proyecto.titulo,
        'estado': proyecto.estado,
        'fecha_creacion': proyecto.fecha_creacion.isoformat() if proyecto.fecha_creacion else None,
        'fecha_modificacion': proyecto.fecha_modificacion.isoformat() if hasattr(proyecto, 'fecha_modificacion') and proyecto.fecha_modificacion else None,
        'descripcion': getattr(proyecto, 'descripcion', ''),
    }
    
    # Agregar instancias gestoras del proyecto
    if hasattr(proyecto, 'instancia_gestora'):
        proyecto_data['instancias_gestoras'] = [
            {
                'id': ig.id,
                'codigo': ig.codigo,
                'instancia': ig.instancia
            }
            for ig in proyecto.instancia_gestora.all()
        ]
    
    return Response({
        'proyecto': proyecto_data,
        'acceso': acceso,
        'nivel_acceso': nivel,
        'nivel_acceso_display': permission_service.obtener_nombre_nivel_acceso(nivel),
        'puede_ver': permission_service.puede_ver_proyecto(request.user, proyecto),
        'puede_editar': permission_service.puede_editar_proyecto(request.user, proyecto),
        'puede_administrar': permission_service.puede_administrar_proyecto(request.user, proyecto),
        'detalles_acceso': _obtener_detalles_acceso(permission_service, request.user, proyecto)
    })

def _obtener_detalles_acceso(permission_service, usuario, proyecto):
    """Obtener detalles específicos del acceso"""
    detalles = {
        'por_instancia': False,
        'por_permiso_especifico': False,
        'instancias_con_acceso': [],
        'nivel_maximo_instancia': permission_service.SIN_ACCESO
    }
    
    # Verificar acceso por instancias
    instancias_usuario = permission_service.obtener_instancias_gestoras_usuario(usuario)
    instancias_proyecto = permission_service._obtener_instancias_del_proyecto(proyecto)
    
    for user_instancia in instancias_usuario:
        if user_instancia.instancia_gestora_id in instancias_proyecto:
            detalles['por_instancia'] = True
            detalles['instancias_con_acceso'].append({
                'id': user_instancia.instancia_gestora_id,
                'nivel_acceso': user_instancia.nivel_acceso,
                'nivel_acceso_display': permission_service.obtener_nombre_nivel_acceso(user_instancia.nivel_acceso)
            })
            if user_instancia.nivel_acceso > detalles['nivel_maximo_instancia']:
                detalles['nivel_maximo_instancia'] = user_instancia.nivel_acceso
    
    # Verificar acceso por permiso específico
    from ..models import PermisoProyectoEspecifico
    from django.utils import timezone
    
    permiso_especifico = PermisoProyectoEspecifico.objects.filter(
        usuario=usuario, 
        proyecto=proyecto, 
        activo=True
    ).first()
    
    if permiso_especifico:
        detalles['por_permiso_especifico'] = True
        detalles['permiso_especifico'] = {
            'tipo_acceso': permiso_especifico.tipo_acceso,
            'tipo_acceso_display': permission_service.obtener_nombre_nivel_acceso(permiso_especifico.tipo_acceso),
            'fecha_asignacion': permiso_especifico.fecha_asignacion.isoformat() if permiso_especifico.fecha_asignacion else None,
            'fecha_expiracion': permiso_especifico.fecha_expiracion.isoformat() if permiso_especifico.fecha_expiracion else None,
            'activo': permiso_especifico.activo
        }
    
    return detalles

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
            models.Q(titulo__icontains=search) |
            models.Q(descripcion__icontains=search)
        )
    
    # Ordenamiento
    sort_by = request.GET.get('sort_by', 'fecha_creacion')
    sort_order = request.GET.get('sort_order', 'desc')
    
    if sort_order == 'desc':
        sort_by = f'-{sort_by}'
    
    proyectos = proyectos.order_by(sort_by)
    
    # Paginación
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size
    
    proyectos_paginados = proyectos[start:end]
    
    proyectos_data = []
    for proyecto in proyectos_paginados:
        nivel = permission_service.obtener_nivel_acceso_proyecto(request.user, proyecto)
        
        proyecto_info = {
            'id': proyecto.id,
            'codigo': proyecto.codigo,
            'titulo': proyecto.titulo,
            'estado': proyecto.estado,
            'fecha_creacion': proyecto.fecha_creacion.isoformat() if proyecto.fecha_creacion else None,
            'nivel_acceso': nivel,
            'nivel_acceso_display': permission_service.obtener_nombre_nivel_acceso(nivel),
            'descripcion': getattr(proyecto, 'descripcion', '')[:100]  # Limitar descripción
        }
        
        # Agregar información de instancias si está disponible
        if hasattr(proyecto, 'instancia_gestora'):
            proyecto_info['instancias'] = [
                {
                    'id': ig.id,
                    'codigo': ig.codigo,
                    'instancia': ig.instancia
                }
                for ig in proyecto.instancia_gestora.all()[:3]  # Limitar a 3 instancias
            ]
            proyecto_info['total_instancias'] = proyecto.instancia_gestora.count()
        
        proyectos_data.append(proyecto_info)
    
    # Información de paginación extendida
    total_proyectos = proyectos.count()
    total_paginas = (total_proyectos + page_size - 1) // page_size
    
    return Response({
        'proyectos': proyectos_data,
        'paginacion': {
            'pagina_actual': page,
            'tamano_pagina': page_size,
            'total_proyectos': total_proyectos,
            'total_paginas': total_paginas,
            'has_previous': page > 1,
            'has_next': page < total_paginas,
            'previous_page': page - 1 if page > 1 else None,
            'next_page': page + 1 if page < total_paginas else None
        },
        'filtros': {
            'estado': estado,
            'search': search,
            'sort_by': sort_by.replace('-', '') if sort_by.startswith('-') else sort_by,
            'sort_order': 'desc' if sort_by.startswith('-') else 'asc'
        },
        'estadisticas': {
            'proyectos_por_estado': dict(proyectos.values_list('estado').annotate(count=models.Count('id'))),
            'proyectos_por_nivel_acceso': {
                'lectura': len([p for p in proyectos_data if p['nivel_acceso'] >= permission_service.LECTURA]),
                'edicion': len([p for p in proyectos_data if p['nivel_acceso'] >= permission_service.EDICION]),
                'administracion': len([p for p in proyectos_data if p['nivel_acceso'] >= permission_service.ADMINISTRACION]),
            }
        }
    })