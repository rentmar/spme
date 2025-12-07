# views.py
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.contrib.auth import get_user_model
from spme_mensajes.models import MensajeUsuario, TipoMensaje
from ..serializers.mensajeria_serializers import MensajeCreateSerializer

#from .models import MensajeUsuario, TipoMensaje
#from .serializers import MensajeCreateSerializer

User = get_user_model()

class CrearMensajeView(CreateAPIView):
    """
    Endpoint para crear mensajes.
    El remitente se extrae automáticamente del JWT.
    
    POST /api/mensajes/
    
    Ejemplo de solicitud:
    {
        "destinatario_id": 2,
        "asunto": "Reunión importante",
        "contenido": "Hola, tenemos reunión mañana a las 10 AM.",
        "tipo": "privado",
        "prioridad": 2,
        "actividad_id": 1,
        "proyecto_id": 1,
        "icono": "📅"
    }
    
    Para mensajes del sistema (solo administradores):
    {
        "destinatario_id": 2,
        "asunto": "Notificación del sistema",
        "contenido": "Su actividad ha sido actualizada.",
        "tipo": "sistema",
        "prioridad": 3
    }
    """
    serializer_class = MensajeCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        # El remitente se asigna automáticamente en el serializer desde request.user
        return serializer.save()
    
    def create(self, request, *args, **kwargs):
        # Validar permisos especiales para mensajes del sistema
        if request.data.get('tipo') == TipoMensaje.SISTEMA:
            if not (request.user.is_staff or request.user.is_superuser):
                return Response({
                    'success': False,
                    'message': 'No tienes permisos para enviar mensajes del sistema'
                }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    mensaje = serializer.save()
                
                # Construir respuesta
                response_data = self._build_response_data(mensaje)
                
                return Response({
                    'success': True,
                    'message': 'Mensaje creado exitosamente',
                    'data': response_data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'success': False,
                    'error': str(e),
                    'message': 'Error al crear el mensaje'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'success': False,
            'errors': serializer.errors,
            'message': 'Error de validación'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def _build_response_data(self, mensaje):
        """Construye los datos de respuesta del mensaje"""
        return {
            'id': mensaje.id,
            'message_id': mensaje.message_id,
            'tipo': mensaje.tipo,
            'tipo_display': mensaje.get_tipo_display(),
            'asunto': mensaje.asunto,
            'contenido': mensaje.contenido,
            'estado': mensaje.estado,
            'estado_display': mensaje.get_estado_display(),
            'prioridad': mensaje.prioridad,
            'fecha_envio': mensaje.fecha_envio,
            'fecha_expiracion': mensaje.fecha_expiracion,
            'icono': mensaje.icono,
            'accion_url': mensaje.accion_url,
            'accion_texto': mensaje.accion_texto,
            'actividad_id': mensaje.actividad_id,
            'proyecto_id': mensaje.proyecto_id,
            'metadata': mensaje.metadata,
            'referencia_id': mensaje.referencia_id,
            'routing_key': mensaje.routing_key,
            'remitente': {
                'id': mensaje.remitente.id if mensaje.remitente else None,
                'username': mensaje.remitente.username if mensaje.remitente else 'Sistema',
                'nombre_completo': mensaje.remitente.get_full_name() if mensaje.remitente and hasattr(mensaje.remitente, 'get_full_name') else 'Sistema',
            } if mensaje.remitente else {
                'id': None,
                'username': 'Sistema',
                'nombre_completo': 'Sistema',
            },
            'destinatario': {
                'id': mensaje.destinatario.id,
                'username': mensaje.destinatario.username,
                'nombre_completo': mensaje.destinatario.get_full_name() if hasattr(mensaje.destinatario, 'get_full_name') else mensaje.destinatario.username,
            }
        }


class CrearMensajeSistemaView(APIView):
    """
    Endpoint específico para mensajes del sistema.
    Solo para administradores/staff.
    
    POST /api/mensajes/sistema/
    
    Ejemplo:
    {
        "destinatario_id": 2,
        "asunto": "Actualización del sistema",
        "contenido": "Se ha aplicado una actualización importante.",
        "prioridad": 2,
        "actividad_id": 1
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        # Verificar permisos de administrador
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({
                'success': False,
                'message': 'Solo administradores pueden enviar mensajes del sistema'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Forzar tipo sistema
        data = request.data.copy()
        data['tipo'] = TipoMensaje.SISTEMA
        
        serializer = MensajeCreateSerializer(data=data, context={'request': request})
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    mensaje = serializer.save()
                
                response_data = {
                    'id': mensaje.id,
                    'message_id': mensaje.message_id,
                    'asunto': mensaje.asunto,
                    'contenido': mensaje.contenido,
                    'estado': mensaje.estado,
                    'tipo': mensaje.tipo,
                    'tipo_display': mensaje.get_tipo_display(),
                    'prioridad': mensaje.prioridad,
                    'fecha_envio': mensaje.fecha_envio,
                    'icono': mensaje.icono,
                    'remitente': {
                        'id': None,
                        'username': 'Sistema',
                        'nombre_completo': 'Sistema',
                    },
                    'destinatario': {
                        'id': mensaje.destinatario.id,
                        'username': mensaje.destinatario.username,
                        'nombre_completo': mensaje.destinatario.get_full_name() if hasattr(mensaje.destinatario, 'get_full_name') else mensaje.destinatario.username,
                    }
                }
                
                return Response({
                    'success': True,
                    'message': 'Mensaje del sistema creado exitosamente',
                    'data': response_data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'success': False,
                    'error': str(e),
                    'message': 'Error al crear el mensaje del sistema'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'success': False,
            'errors': serializer.errors,
            'message': 'Error de validación'
        }, status=status.HTTP_400_BAD_REQUEST)


class CrearMensajeMultipleView(APIView):
    """
    Endpoint para crear múltiples mensajes a la vez.
    El remitente se extrae del JWT.
    
    POST /api/mensajes/multiple/
    
    Ejemplo:
    {
        "destinatarios_ids": [2, 3, 4],
        "asunto": "Notificación grupal",
        "contenido": "Este es un mensaje para todos.",
        "tipo": "recordatorio",
        "prioridad": 1
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        destinatarios_ids = request.data.get('destinatarios_ids', [])
        asunto = request.data.get('asunto')
        contenido = request.data.get('contenido')
        
        if not destinatarios_ids:
            return Response({
                'success': False,
                'message': 'Debe especificar al menos un destinatario'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not asunto or not contenido:
            return Response({
                'success': False,
                'message': 'El asunto y contenido son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        mensajes_creados = []
        errores = []
        
        for destinatario_id in destinatarios_ids:
            try:
                mensaje_data = {
                    'destinatario_id': destinatario_id,
                    'asunto': asunto,
                    'contenido': contenido,
                    'tipo': request.data.get('tipo', 'privado'),
                    'prioridad': request.data.get('prioridad', 1),
                    'actividad_id': request.data.get('actividad_id'),
                    'proyecto_id': request.data.get('proyecto_id'),
                    'icono': request.data.get('icono', '📧'),
                    'accion_url': request.data.get('accion_url'),
                    'accion_texto': request.data.get('accion_texto'),
                    'metadata': request.data.get('metadata', {}),
                }
                
                serializer = MensajeCreateSerializer(data=mensaje_data, context={'request': request})
                
                if serializer.is_valid():
                    mensaje = serializer.save()
                    mensajes_creados.append({
                        'message_id': mensaje.message_id,
                        'destinatario_id': destinatario_id,
                        'destinatario_username': mensaje.destinatario.username
                    })
                else:
                    errores.append({
                        'destinatario_id': destinatario_id,
                        'errors': serializer.errors
                    })
                    
            except Exception as e:
                errores.append({
                    'destinatario_id': destinatario_id,
                    'error': str(e)
                })
        
        if mensajes_creados:
            return Response({
                'success': True,
                'message': f'Se crearon {len(mensajes_creados)} mensajes exitosamente',
                'remitente': {
                    'id': request.user.id,
                    'username': request.user.username
                },
                'mensajes_creados': mensajes_creados,
                'errores': errores if errores else None,
                'total_enviados': len(mensajes_creados),
                'total_errores': len(errores)
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': 'No se pudo crear ningún mensaje',
                'errores': errores
            }, status=status.HTTP_400_BAD_REQUEST)