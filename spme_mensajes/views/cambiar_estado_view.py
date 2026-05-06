# spme/spme_mensajes/views/cambiar_estado_view.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from ..models import MensajeUsuario
from ..serializers.cambiar_estado_serializer import CambiarEstadoMensajesSerializer

class CambiarEstadoMensajesView(APIView):
    """
    API para cambiar el estado de múltiples mensajes
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        """
        Cambia el estado de múltiples mensajes
        
        PATCH /api/mensajes/cambiar-estado/
        
        Body:
        {
            "ids": [1, 2, 3],
            "estado": "leido"
        }
        """
        serializer = CambiarEstadoMensajesSerializer(
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
                    {'error': f'Error al cambiar estado: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)