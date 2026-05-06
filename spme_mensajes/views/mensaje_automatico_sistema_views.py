# en views.py o api/views.py
# spme/spme_mensajes/views/mensaje_automatico_sistema_views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db import transaction
import uuid

from spme_mensajes.models import Usuario, MensajeUsuario, TipoMensaje, EstadoMensaje
from ..serializers.mensaje_automatico_sistema_serializer import MensajeUsuarioSerializer

#from .models import MensajeUsuario, Usuario, TipoMensaje, EstadoMensaje
#from .serializers import MensajeUsuarioSerializer

class CrearMensajeAutomaticoSistemaView(APIView):
    """
    Endpoint para crear mensajes del sistema sin autenticación.
    Solo permite crear mensajes con tipo 'sistema', 'alerta', 'recordatorio', 
    'reprogramacion', 'retraso'
    """
    
    # Deshabilitar autenticación para este endpoint
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        """
        Crear un mensaje del sistema
        Ejemplo de datos:
        {
            "destinatario_id": 6,
            "asunto": "Actividad completada",
            "contenido": "La actividad 'Revisión de diseño' ha sido completada",
            "tipo": "sistema",
            "prioridad": 2,
            "actividad_id": 123,
            "proyecto_id": 456,
            "icono": "✅",
            "accion_url": "/actividades/123/",
            "accion_texto": "Ver actividad"
        }
        """
        try:
            # Validar que el tipo sea válido para mensajes del sistema
            tipo = request.data.get('tipo', 'sistema')
            tipos_permitidos = [
                TipoMensaje.SISTEMA,
                TipoMensaje.ALERTA,
                TipoMensaje.RECORDATORIO,
                TipoMensaje.REPROGRAMACION,
                TipoMensaje.RETRASO
            ]
            
            if tipo not in tipos_permitidos:
                return Response({
                    'error': f'Tipo no permitido. Tipos válidos: {", ".join(tipos_permitidos)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar destinatario
            destinatario_id = request.data.get('destinatario_id')
            if not destinatario_id:
                return Response({
                    'error': 'destinatario_id es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                destinatario = Usuario.objects.get(id=destinatario_id, is_active=True)
            except Usuario.DoesNotExist:
                return Response({
                    'error': 'Destinatario no encontrado o no activo'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Preparar datos para el mensaje
            mensaje_data = {
                'tipo': tipo,
                'destinatario': destinatario,
                'asunto': request.data.get('asunto', 'Notificación del Sistema'),
                'contenido': request.data.get('contenido', ''),
                'prioridad': request.data.get('prioridad', 2),
                'estado': EstadoMensaje.NO_LEIDO,
                'actividad_id': request.data.get('actividad_id'),
                'proyecto_id': request.data.get('proyecto_id'),
                'icono': request.data.get('icono', self._get_icono_por_tipo(tipo)),
                'accion_url': request.data.get('accion_url'),
                'accion_texto': request.data.get('accion_texto'),
                'metadata': request.data.get('metadata', {}),
                'routing_key': request.data.get('routing_key', f'sistema.{tipo}')
            }
            
            # Agregar campos de fecha si se proporcionan
            if 'fecha_envio' in request.data:
                mensaje_data['fecha_envio'] = request.data['fecha_envio']
            if 'fecha_expiracion' in request.data:
                mensaje_data['fecha_expiracion'] = request.data['fecha_expiracion']
            
            # Crear el mensaje del sistema
            with transaction.atomic():
                mensaje = MensajeUsuario.objects.create(**mensaje_data)
                
                # Generar referencia si se proporciona actividad o proyecto
                referencia = None
                if mensaje.actividad_id:
                    referencia = f"ACT-{mensaje.actividad_id}"
                elif mensaje.proyecto_id:
                    referencia = f"PROY-{mensaje.proyecto_id}"
                
                if referencia:
                    mensaje.referencia_id = referencia
                    mensaje.save()
            
            # Serializar respuesta
            serializer = MensajeUsuarioSerializer(mensaje)
            
            return Response({
                'success': True,
                'message': 'Mensaje del sistema creado exitosamente',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al crear mensaje: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_icono_por_tipo(self, tipo):
        """Obtener icono por defecto según el tipo de mensaje"""
        iconos = {
            TipoMensaje.SISTEMA: '🔔',
            TipoMensaje.ALERTA: '⚠️',
            TipoMensaje.RECORDATORIO: '⏰',
            TipoMensaje.REPROGRAMACION: '🔄',
            TipoMensaje.RETRASO: '⏳',
        }
        return iconos.get(tipo, '📧')