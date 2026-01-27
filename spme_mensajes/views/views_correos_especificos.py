"""
Vistas específicas para probar los tres tipos de correos
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from ..services.correos_especificos_service import CorreosEspecificosService


@api_view(['POST'])
@permission_classes([AllowAny])
def prueba_correo_prueba(request):
    """
    Endpoint para probar correo de prueba del sistema
    POST /api/mensajes/correos/prueba-sistema/
    
    Body:
    {
        "email": "test@example.com",
        "nombre": "Usuario Test",
        "contexto_adicional": {}  # opcional
    }
    """
    try:
        data = request.data
        
        if not data.get('email'):
            return Response({
                'success': False,
                'error': 'El campo email es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        resultado = CorreosEspecificosService.enviar_prueba_sistema(
            email=data['email'],
            nombre_usuario=data.get('nombre'),
            contexto_adicional=data.get('contexto_adicional', {})
        )
        
        if resultado['success']:
            return Response({
                'success': True,
                'message': 'Correo de prueba programado',
                'task_id': resultado['task_id'],
                'email': resultado['email'],
                'tipo': 'prueba_sistema'
            }, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({
                'success': False,
                'error': resultado.get('error')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def prueba_correo_pendiente(request):
    """
    Endpoint para probar correo de solicitud pendiente
    POST /api/mensajes/correos/solicitud-pendiente/
    
    Body:
    {
        "emails": ["revisor1@example.com", "revisor2@example.com"],
        "datos_solicitud": {
            "codigo": "SOL-2024-001",
            "titulo": "Solicitud de prueba",
            "solicitante": "Juan Pérez",
            "tipo": "General",
            "prioridad": "alta",
            "descripcion": "Descripción de prueba",
            "url_revision": "http://localhost:8000/solicitudes/1"
        }
    }
    """
    try:
        data = request.data
        
        if not data.get('emails'):
            return Response({
                'success': False,
                'error': 'El campo emails es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not data.get('datos_solicitud'):
            return Response({
                'success': False,
                'error': 'El campo datos_solicitud es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Usar datos de ejemplo si no se proporcionan todos
        datos_solicitud = data['datos_solicitud']
        if not datos_solicitud.get('codigo'):
            datos_solicitud['codigo'] = f"SOL-TEST-{timezone.now().strftime('%Y%m%d')}"
        if not datos_solicitud.get('fecha_solicitud'):
            datos_solicitud['fecha_solicitud'] = timezone.now()
        
        resultado = CorreosEspecificosService.notificar_solicitud_pendiente(
            emails_revisores=data['emails'],
            datos_solicitud=datos_solicitud,
            contexto_adicional=data.get('contexto_adicional', {})
        )
        
        if resultado['success']:
            return Response({
                'success': True,
                'message': 'Notificación de solicitud pendiente programada',
                'task_id': resultado['task_id'],
                'solicitud_codigo': resultado['solicitud_codigo'],
                'tipo': 'solicitud_pendiente'
            }, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({
                'success': False,
                'error': resultado.get('error')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def prueba_correo_aprobada(request):
    """
    Endpoint para probar correo de solicitud aprobada
    POST /api/mensajes/correos/solicitud-aprobada/
    
    Body:
    {
        "emails": ["solicitante@example.com", "interesado@example.com"],
        "datos_aprobacion": {
            "codigo": "SOL-2024-001",
            "titulo": "Solicitud aprobada de prueba",
            "solicitante_nombre": "Juan Pérez",
            "aprobador_nombre": "María González",
            "numero_aprobacion": "APR-2024-001",
            "url_detalles": "http://localhost:8000/solicitudes/1"
        }
    }
    """
    try:
        data = request.data
        
        if not data.get('emails'):
            return Response({
                'success': False,
                'error': 'El campo emails es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not data.get('datos_aprobacion'):
            return Response({
                'success': False,
                'error': 'El campo datos_aprobacion es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Usar datos de ejemplo si no se proporcionan todos
        datos_aprobacion = data['datos_aprobacion']
        if not datos_aprobacion.get('codigo'):
            datos_aprobacion['codigo'] = f"APR-TEST-{timezone.now().strftime('%Y%m%d')}"
        if not datos_aprobacion.get('fecha_aprobacion'):
            datos_aprobacion['fecha_aprobacion'] = timezone.now()
        
        resultado = CorreosEspecificosService.notificar_solicitud_aprobada(
            emails_destinatarios=data['emails'],
            datos_aprobacion=datos_aprobacion,
            contexto_adicional=data.get('contexto_adicional', {})
        )
        
        if resultado['success']:
            return Response({
                'success': True,
                'message': 'Notificación de solicitud aprobada programada',
                'task_id': resultado['task_id'],
                'solicitud_codigo': resultado['solicitud_codigo'],
                'tipo': 'solicitud_aprobada'
            }, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({
                'success': False,
                'error': resultado.get('error')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def ejemplos_datos(request):
    """
    Obtiene ejemplos de datos para los correos
    GET /api/mensajes/correos/ejemplos/
    """
    ejemplos = {
        'solicitud_pendiente': CorreosEspecificosService.ejemplo_solicitud_pendiente(),
        'solicitud_aprobada': CorreosEspecificosService.ejemplo_solicitud_aprobada(),
        'notas': 'Estos son ejemplos de datos que puedes usar para probar los endpoints'
    }
    
    return Response({
        'success': True,
        'data': ejemplos
    })

# Agrega esta función al final del archivo
@api_view(['POST'])
@permission_classes([AllowAny])
def prueba_correo_nuevo_mensaje(request):
    """
    Endpoint para probar correo de nuevo mensaje
    POST /api/mensajes/correos/nuevo-mensaje/
    """
    try:
        data = request.data
        
        if not data.get('destinatarios'):
            return Response({
                'success': False,
                'error': 'El campo destinatarios es requerido'
            }, status=400)
        
        if not data.get('asunto_mensaje'):
            return Response({
                'success': False,
                'error': 'El campo asunto_mensaje es requerido'
            }, status=400)
        
        if not data.get('contenido_mensaje'):
            return Response({
                'success': False,
                'error': 'El campo contenido_mensaje es requerido'
            }, status=400)
        
        resultado = CorreosEspecificosService.notificar_nuevo_mensaje(data)
        
        if resultado['success']:
            return Response(resultado, status=202)
        else:
            return Response(resultado, status=500)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)