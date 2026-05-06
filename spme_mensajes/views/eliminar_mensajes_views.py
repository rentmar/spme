# spme/spme_mensajes/views/eliminar_mensajes_views.py
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from spme_mensajes.models import MensajeUsuario
from ..serializers.eliminar_mensajes_serializer import MensajeEliminarSerializer

class MensajeViewSet(viewsets.GenericViewSet):
    """
    ViewSet para operaciones básicas con mensajes
    """
    permission_classes = [IsAuthenticated]
    queryset = MensajeUsuario.objects.all()
    
    @action(detail=False, methods=['delete'], url_path='eliminar-mensajes')
    def eliminar_mensajes(self, request):
        """
        Elimina múltiples mensajes
        
        DELETE /api/mensajes/eliminar-mensajes/
        
        Body:
        {
            "ids": [1, 2, 3],
            "tipo_eliminacion": "soft"  # opcional: "soft" o "hard"
        }
        """
        serializer = MensajeEliminarSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    resultado = serializer.save()
                return Response(resultado, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    {'error': f'Error al eliminar mensajes: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar_mensaje(self, request, pk=None):
        """
        Elimina un mensaje específico
        
        DELETE /api/mensajes/{id}/eliminar/
        
        Params opcionales:
        ?tipo_eliminacion=hard
        """
        try:
            mensaje = MensajeUsuario.objects.get(
                pk=pk,
                destinatario=request.user
            )
        except MensajeUsuario.DoesNotExist:
            return Response(
                {'error': 'Mensaje no encontrado o no tienes permiso'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        tipo_eliminacion = request.query_params.get('tipo_eliminacion', 'soft')
        
        try:
            if tipo_eliminacion == 'hard':
                mensaje.delete()
                mensaje_accion = 'eliminado permanentemente'
            else:
                mensaje.eliminar()
                mensaje_accion = 'marcado como eliminado'
            
            return Response({
                'mensaje': f'Mensaje {mensaje_accion} correctamente',
                'id': pk,
                'tipo_eliminacion': tipo_eliminacion
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Error al eliminar mensaje: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )