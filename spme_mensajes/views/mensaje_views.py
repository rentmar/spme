#Vistas para mensajería interna con autenticación JWT
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..services.mensaje_service import MensajeService
from ..serializers.mensaje_serializer import (
    MensajeSerializer,
    CrearMensajeSerializer,
    ActualizarEstadoMensajeSerializer,
    MarcarVariosLeidoSerializer,
    ConteoMensajesSerializer,
    BuscarMensajesSerializer,
    CrearMensajeMultipleSerializer,
    MensajesEnviadosSerializer,
)

from ..services.mensaje_service import MensajeRepository
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# BANDEJA DE ENTRADA
# ============================================================================

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def obtener_bandeja_entrada(request):
    """
    Obtiene la bandeja de entrada del usuario autenticado
    
    GET /api/mensajes/bandeja/
    
    Query Params:
        estado: Filtro por estado (no_leido, leido, archivado)
        tipo: Filtro por tipo (privado, sistema, alerta, actividad, recordatorio, reprogramacion, retraso)
        limit: Límite de resultados (default: 50, max: 100)
        offset: Offset para paginación (default: 0)
    
    Returns:
        {
            "success": true,
            "data": {
                "mensajes": [...],
                "paginacion": {...},
                "estadisticas": {...}
            }
        }
    """
    try:
        usuario = request.user
        
        # Obtener parámetros de filtro
        filtros = {
            'estado': request.GET.get('estado'),
            'tipo': request.GET.get('tipo'),
            'limit': int(request.GET.get('limit', 50)),
            'offset': int(request.GET.get('offset', 0)),
        }
        
        # Validar límite
        if filtros['limit'] > 100:
            filtros['limit'] = 100
        
        # Obtener bandeja
        resultado = MensajeService.obtener_bandeja_entrada(
            destinatario_id=usuario.pk,
            filtros=filtros
        )
        
        return Response({
            'success': True,
            'data': resultado
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ============================================================================
# OPERACIONES CON MENSAJES INDIVIDUALES
# ============================================================================

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def obtener_mensaje(request, mensaje_id):
    """
    Obtiene un mensaje específico y lo marca como leído
    
    GET /api/mensajes/{mensaje_id}/
    
    Returns:
        {
            "success": true,
            "data": {...}
        }
    """
    try:
        usuario = request.user
        
        mensaje_data = MensajeService.obtener_mensaje(mensaje_id, usuario.pk)
        
        if not mensaje_data:
            return Response({
                'success': False,
                'error': 'Mensaje no encontrado o no tienes permiso'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'data': mensaje_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def crear_mensaje_privado(request):
    """
    Envía un mensaje privado a otro usuario
    
    POST /api/mensajes/enviar/
    
    Body:
    {
        "destinatario_id": 2,
        "asunto": "Asunto del mensaje",
        "contenido": "Contenido del mensaje",
        "prioridad": 1,  # 1=baja, 2=media, 3=alta
        "metadata": {}
    }
    
    Returns:
        {
            "success": true,
            "data": {...},
            "message": "Mensaje enviado exitosamente"
        }
    """
    try:
        usuario = request.user
        data = request.data.copy()
        
        # Validar datos requeridos
        if 'destinatario_id' not in data:
            return Response({
                'success': False,
                'error': 'El campo destinatario_id es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if 'contenido' not in data:
            return Response({
                'success': False,
                'error': 'El campo contenido es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Si no se especifica asunto, usar uno por defecto
        if 'asunto' not in data or not data['asunto']:
            data['asunto'] = 'Sin asunto'
        
        # Enviar mensaje
        resultado = MensajeService.enviar_mensaje_privado(
            remitente_id=usuario.pk,
            destinatario_id=data['destinatario_id'],
            asunto=data['asunto'],
            contenido=data['contenido'],
            metadata=data.get('metadata', {})
        )
        
        if resultado['success']:
            return Response({
                'success': True,
                'data': resultado,
                'message': 'Mensaje enviado exitosamente'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'error': resultado.get('error')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Envio de mensajes masivos con remitente
# Archivo: mensaje_views.py (agregar después de la función crear_mensaje_privado)

# Reemplazar la función crear_mensaje_multiple en mensaje_views.py con esta versión mejorada

# En mensaje_views.py, reemplazar la función crear_mensaje_multiple con esta versión:

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def crear_mensaje_multiple(request):
    """
    Envía un mensaje a múltiples destinatarios
    
    POST /api/mensajes/remite-enviar-multiple/
    
    Body:
    {
        "destinatarios_ids": [2, 3, 4],
        "asunto": "Mensaje para el equipo",
        "contenido": "Contenido del mensaje para todos",
        "tipo": "privado",        # ← Nuevo campo opcional
        "prioridad": 3,           # ← Ahora se guardará correctamente
        "metadata": {}
    }
    
    Returns:
        {
            "success": true,
            "data": {...},
            "message": "Mensaje enviado a 3 destinatarios"
        }
    """
    try:
        usuario = request.user
        
        # Validar datos con serializer
        serializer = CrearMensajeMultipleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Usar el nuevo método de servicio
        resultado = MensajeService.enviar_mensaje_multiple_remitente(
            remitente_id=usuario.pk,
            destinatarios_ids=data['destinatarios_ids'],
            asunto=data['asunto'],
            contenido=data['contenido'],
            tipo=data.get('tipo'),           # ← Pasar tipo
            prioridad=data.get('prioridad'),  # ← Pasar prioridad
            metadata=data.get('metadata', {})
        )
        
        if resultado['success']:
            status_code = status.HTTP_201_CREATED 
            if resultado['data'].get('errores'):
                status_code = status.HTTP_207_MULTI_STATUS
            
            mensaje_respuesta = resultado['message']
            if resultado['data'].get('errores'):
                mensaje_respuesta += f' (con {len(resultado["data"]["errores"])} error(es))'
            
            return Response({
                'success': True,
                'data': resultado['data'],
                'message': mensaje_respuesta
            }, status=status_code)
        else:
            return Response({
                'success': False,
                'error': resultado.get('error'),
                'errores_detallados': resultado.get('errores_detallados')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Reemplazar la función obtener_mensajes_enviados en mensaje_views.py con esta versión mejorada

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def obtener_mensajes_enviados(request):
    """
    Obtiene todos los mensajes enviados por el usuario autenticado
    
    GET /api/mensajes/enviados/
    
    Query Params:
        destinatario_id: Filtrar por destinatario específico (opcional)
        tipo: Filtro por tipo (privado, sistema, etc.)
        limit: Límite de resultados (default: 50, max: 100)
        offset: Offset para paginación (default: 0)
    
    Returns:
        {
            "success": true,
            "data": {
                "mensajes": [...],
                "paginacion": {...},
                "estadisticas": {...}
            }
        }
    """
    try:
        usuario = request.user
        
        # Validar parámetros con serializer
        serializer = MensajesEnviadosSerializer(data=request.GET)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        filtros = serializer.validated_data
        
        # Obtener mensajes enviados usando el repositorio
        mensajes = MensajeRepository.obtener_mensajes_enviados(
            remitente_id=usuario.pk,
            filtros=filtros
        )
        
        # Contar total de mensajes enviados
        conteos = MensajeRepository.contar_mensajes_enviados(
            remitente_id=usuario.pk,
            filtros=filtros
        )
        
        # Formatear respuesta
        resultado = {
            'mensajes': [msg.obtener_datos_contexto() for msg in mensajes],
            'paginacion': {
                'total': conteos['total'],
                'limit': filtros['limit'],
                'offset': filtros['offset'],
                'has_more': (filtros['offset'] + filtros['limit']) < conteos['total']
            },
            'estadisticas': conteos
        }
        
        return Response({
            'success': True,
            'data': resultado
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def actualizar_estado_mensaje(request, mensaje_id):
    """
    Actualiza el estado de un mensaje
    
    PUT /api/mensajes/{mensaje_id}/estado/
    
    Body:
    {
        "estado": "leido"  # o "no_leido", "archivado", "eliminado"
    }
    
    Returns:
        {
            "success": true,
            "data": {...},
            "message": "Mensaje marcado como leido"
        }
    """
    try:
        usuario = request.user
        
        # Validar datos
        serializer = ActualizarEstadoMensajeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        nuevo_estado = serializer.validated_data['estado']
        
        # Actualizar estado
        mensaje = MensajeService.actualizar_estado_mensaje(
            mensaje_id=mensaje_id,
            destinatario_id=usuario.pk,
            nuevo_estado=nuevo_estado
        )
        
        if not mensaje:
            return Response({
                'success': False,
                'error': 'Mensaje no encontrado o no tienes permiso'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'data': {
                'mensaje_id': mensaje.pk,
                'estado': mensaje.estado,
                'message_id': mensaje.message_id
            },
            'message': f'Mensaje marcado como {nuevo_estado}'
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ============================================================================
# OPERACIONES MASIVAS
# ============================================================================

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def marcar_varios_leido(request):
    """
    Marca varios mensajes como leídos
    
    POST /api/mensajes/marcar-leidos/
    
    Body:
    {
        "mensaje_ids": [1, 2, 3]
    }
    
    Returns:
        {
            "success": true,
            "data": {...},
            "message": "3 mensajes marcados como leídos"
        }
    """
    try:
        usuario = request.user
        
        # Validar datos
        serializer = MarcarVariosLeidoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        mensaje_ids = serializer.validated_data['mensaje_ids']
        
        # Marcar como leídos
        actualizados = MensajeService.marcar_varios_como_leido(mensaje_ids, usuario.pk)
        
        return Response({
            'success': True,
            'data': {
                'actualizados': actualizados,
                'total_solicitados': len(mensaje_ids)
            },
            'message': f'{actualizados} mensajes marcados como leídos'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def marcar_todos_leido(request):
    """
    Marca todos los mensajes no leídos como leídos
    
    POST /api/mensajes/marcar-todos-leidos/
    
    Returns:
        {
            "success": true,
            "data": {...},
            "message": "10 mensajes marcados como leídos"
        }
    """
    try:
        usuario = request.user
        
        # Obtener estadísticas para saber cuántos hay no leídos
        estadisticas = MensajeService.obtener_estadisticas(usuario.pk)
        no_leidos = estadisticas.get('no_leidos', 0)
        
        if no_leidos == 0:
            return Response({
                'success': True,
                'data': {'actualizados': 0},
                'message': 'No hay mensajes no leídos'
            }, status=status.HTTP_200_OK)
        
        # Obtener todos los IDs de mensajes no leídos
        from ..repositories.mensaje_repository import MensajeRepository
        
        mensajes_no_leidos = MensajeRepository.obtener_mensajes_usuario(
            destinatario_id=usuario.pk,
            estado='no_leido',
            limit=1000
        )
        
        mensaje_ids = [msg.pk for msg in mensajes_no_leidos]
        
        # Marcar como leídos
        actualizados = MensajeService.marcar_varios_como_leido(mensaje_ids, usuario.pk)
        
        return Response({
            'success': True,
            'data': {
                'actualizados': actualizados,
                'total_encontrados': len(mensaje_ids)
            },
            'message': f'{actualizados} mensajes marcados como leídos'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ============================================================================
# BÚSQUEDA Y ESTADÍSTICAS
# ============================================================================

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def buscar_mensajes(request):
    """
    Busca mensajes por contenido
    
    GET /api/mensajes/buscar/
    
    Query Params:
        q: Término de búsqueda (requerido, min: 3 caracteres)
        limit: Límite de resultados (default: 20, max: 100)
    
    Returns:
        {
            "success": true,
            "data": {
                "resultados": [...],
                "total": 5,
                "query": "reunión"
            }
        }
    """
    try:
        usuario = request.user
        
        # Validar datos
        serializer = BuscarMensajesSerializer(data=request.GET)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        query = serializer.validated_data['query']
        limit = serializer.validated_data['limit']
        
        # Buscar mensajes
        resultados = MensajeService.buscar_mensajes(usuario.pk, query, limit)
        
        return Response({
            'success': True,
            'data': {
                'resultados': resultados,
                'total': len(resultados),
                'query': query
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
def obtener_estadisticas(request):
    """
    Obtiene estadísticas de mensajes del usuario
    
    GET /api/mensajes/estadisticas/
    
    Returns:
        {
            "success": true,
            "data": {
                "total": 25,
                "no_leidos": 3,
                "por_estado": {...},
                "por_tipo": {...}
            }
        }
    """
    try:
        usuario = request.user
        
        estadisticas = MensajeService.obtener_estadisticas(usuario.pk)
        
        serializer = ConteoMensajesSerializer(estadisticas)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ============================================================================
# INTEGRACIÓN CON ACTIVIDADES Y PROYECTOS
# ============================================================================

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def enviar_alerta_actividad(request):
    """
    Endpoint para que otros módulos envíen alertas de actividades
    
    POST /api/mensajes/alertas/actividad/
    
    Body:
    {
        "destinatario_id": 1,
        "actividad_id": 100,
        "tipo_evento": "inicio_inminente",
        "datos_actividad": {
            "nombre": "Nombre de la actividad",
            "fecha": "2024-01-25",
            "proyecto_id": 5,
            "url": "/actividades/100",
            "metadata": {},
            "asunto": "Actividad próxima",
            "accion_texto": "Ver Detalles"
        }
    }
    
    Returns:
        {
            "success": true,
            "data": {...},
            "message": "Alerta de actividad enviada"
        }
    """
    try:
        data = request.data
        
        # Validar datos requeridos
        required_fields = ['destinatario_id', 'actividad_id', 'tipo_evento', 'datos_actividad']
        for field in required_fields:
            if field not in data:
                return Response({
                    'success': False,
                    'error': f'El campo {field} es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Enviar alerta
        resultado = MensajeService.enviar_alerta_actividad(
            destinatario_id=data['destinatario_id'],
            actividad_id=data['actividad_id'],
            tipo_evento=data['tipo_evento'],
            datos_actividad=data['datos_actividad']
        )
        
        if resultado['success']:
            return Response({
                'success': True,
                'data': resultado,
                'message': 'Alerta de actividad enviada'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'error': resultado.get('error')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def obtener_mensajes_actividad(request, actividad_id):
    """
    Obtiene mensajes relacionados con una actividad específica
    
    GET /api/mensajes/actividad/{actividad_id}/
    
    Returns:
        {
            "success": true,
            "data": [...]
        }
    """
    try:
        usuario = request.user
        
        mensajes = MensajeService.obtener_mensajes_por_actividad(
            actividad_id=actividad_id,
            destinatario_id=usuario.pk
        )
        
        return Response({
            'success': True,
            'data': mensajes,
            'total': len(mensajes)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def obtener_mensajes_proyecto(request, proyecto_id):
    """
    Obtiene mensajes relacionados con un proyecto específico
    
    GET /api/mensajes/proyecto/{proyecto_id}/
    
    Returns:
        {
            "success": true,
            "data": [...]
        }
    """
    try:
        usuario = request.user
        
        mensajes = MensajeService.obtener_mensajes_por_proyecto(
            proyecto_id=proyecto_id,
            destinatario_id=usuario.pk
        )
        
        return Response({
            'success': True,
            'data': mensajes,
            'total': len(mensajes)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ============================================================================
# ENDPOINTS DE PRUEBA Y EJEMPLOS
# ============================================================================

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def obtener_ejemplos(request):
    """
    Obtiene ejemplos de datos para pruebas
    
    GET /api/mensajes/ejemplos/
    
    Returns:
        {
            "success": true,
            "data": {
                "ejemplo_mensaje_privado": {...},
                "ejemplo_alerta_actividad": {...}
            }
        }
    """
    from django.utils import timezone
    from datetime import timedelta
    
    ejemplos = {
        'ejemplo_mensaje_privado': {
            'remitente_id': 1,
            'destinatario_id': 2,
            'asunto': 'Reunión de coordinación',
            'contenido': 'Hola, te escribo para coordinar la reunión del próximo viernes...',
            'metadata': {
                'tipo_reunion': 'coordinacion',
                'fecha': '2024-01-26',
                'hora': '10:00'
            }
        },
        'ejemplo_alerta_actividad': {
            'destinatario_id': 1,
            'actividad_id': 100,
            'tipo_evento': 'inicio_inminente',
            'datos_actividad': {
                'nombre': 'Revisión de avances del proyecto X',
                'fecha': (timezone.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
                'proyecto_id': 5,
                'url': '/actividades/100',
                'metadata': {
                    'responsable': 'Juan Pérez',
                    'porcentaje_completado': 75
                },
                'asunto': 'Actividad próxima a iniciar',
                'accion_texto': 'Ver Actividad'
            }
        },
        'tipos_evento_soportados': [
            'inicio_inminente',
            'retraso', 
            'reprogramacion',
            'recordatorio',
            'completado',
            'actualizacion'
        ],
        'notas': 'Estos son ejemplos de datos que puedes usar para probar los endpoints'
    }
    
    return Response({
        'success': True,
        'data': ejemplos
    })

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def enviar_mensaje_prueba(request):
    """
    Envía un mensaje de prueba al usuario autenticado
    
    POST /api/mensajes/prueba/
    
    Body (opcional):
    {
        "contenido": "Mensaje personalizado de prueba"
    }
    
    Returns:
        {
            "success": true,
            "data": {...},
            "message": "Mensaje de prueba enviado"
        }
    """
    try:
        usuario = request.user
        contenido = request.data.get('contenido', 'Este es un mensaje de prueba del sistema de mensajería SPME.')
        
        resultado = MensajeService.enviar_notificacion_sistema(
            destinatario_id=usuario.pk,
            contenido=contenido,
            asunto='🧪 Mensaje de Prueba',
            prioridad=1,
            metadata={'tipo': 'prueba', 'timestamp': timezone.now().isoformat()}
        )
        
        if resultado['success']:
            return Response({
                'success': True,
                'data': resultado,
                'message': 'Mensaje de prueba enviado a tu bandeja'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'error': resultado.get('error')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)