from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db import connection
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.utils import timezone

from io import StringIO
import sys
from .models import SystemConfig
from .serializers import (
    SystemConfigSerializer,
    AdminUserSerializer,
    SetupStatusSerializer
)

User = get_user_model()

# ==================== Wizard Endpoints ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def check_setup_status(request):
    """Verifica el estado del sistema para el wizard"""
    try:
        # Verificar tablas de migración
        tables = connection.introspection.table_names()
        db_ready = 'django_migrations' in tables
        
        # Verificar usuario admin
        admin_exists = User.objects.filter(is_superuser=True).exists()
        
        # Verificar si el sistema está inicializado
        config = SystemConfig.get_config()
        
        data = {
            'needs_setup': not (db_ready and admin_exists and config.initialized),
            'database_ready': db_ready,
            'admin_exists': admin_exists,
            'system_initialized': config.initialized
        }
        
        serializer = SetupStatusSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data)
    
    except Exception as e:
        return Response(
            {'error': str(e), 'needs_setup': True},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def run_migrations(request):
    """Ejecuta las migraciones de la base de datos"""
    output = StringIO()
    old_stdout = sys.stdout
    sys.stdout = output
    
    try:
        call_command('migrate', verbosity=1, interactive=False)
        
        # Obtener migraciones aplicadas
        from django.db.migrations.recorder import MigrationRecorder
        migrations = MigrationRecorder.Migration.objects.values_list('app', 'name')
        
        sys.stdout = old_stdout
        
        return Response({
            'success': True,
            'migrations': [f"{app}.{name}" for app, name in migrations],
            'logs': output.getvalue()
        })
    
    except Exception as e:
        sys.stdout = old_stdout
        return Response({
            'success': False,
            'error': str(e),
            'logs': output.getvalue()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_admin_user(request):
    """Crea el usuario administrador inicial"""
    serializer = AdminUserSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            user = serializer.save()
            
            # Marcar sistema como inicializado
            config = SystemConfig.get_config()
            if not config.initialized:
                config.initialized = True
                config.initialized_at = timezone.now()
                config.save()
            
            return Response({
                'success': True,
                'user_id': user.id,
                'username': user.username
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ==================== Configuración del Sistema ====================

@api_view(['GET', 'PUT'])
def system_config(request):
    """Obtiene o actualiza la configuración del sistema"""
    config = SystemConfig.get_config()
    
    if request.method == 'GET':
        serializer = SystemConfigSerializer(config)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = SystemConfigSerializer(config, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def toggle_maintenance_mode(request):
    """Activa/desactiva el modo mantenimiento"""
    config = SystemConfig.get_config()
    config.maintenance_mode = not config.maintenance_mode
    config.save()
    
    return Response({
        'success': True,
        'maintenance_mode': config.maintenance_mode,
        'message': f"Modo mantenimiento {'activado' if config.maintenance_mode else 'desactivado'}"
    })


@api_view(['GET'])
def check_connection(request):
    """
    Endpoint de verificacion 
    """
    try:
        return Response({
            'connected': True,
            'status': 'API operativa',
            'services': {
                'database': True,  # Podrías verificar esto con un query simple
                # Agrega otros servicios que quieras verificar
            }
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'connected': False,
            'error': str(e),
            'status': 'Error en la API'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)