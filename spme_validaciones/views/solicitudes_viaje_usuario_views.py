# views/solicitudes_viaje_usuario_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import logging

from ..services.solicitudes_viaje_usuario_service import (
    SolicitudesViajeUsuarioService
)
from ..serializers.solicitudes_viaje_usuario_serializers import (
    SolicitudesViajeUsuarioResponseSerializer
)

logger = logging.getLogger(__name__)


class SolicitudesViajeUsuarioView(APIView):
    """
    Endpoint especializado para obtener solicitudes de viaje del usuario.
    
    GET /api-valid/solicitudes-viaje/
    """
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, service=None, **kwargs):
        super().__init__(**kwargs)
        self.service = service or SolicitudesViajeUsuarioService()
    
    def get(self, request):
        try:
            usuario_id = request.user.id
            
            logger.info(f"Obteniendo solicitudes de viaje para usuario ID={usuario_id}")
            
            resultado = self.service.obtener_solicitudes_usuario(usuario_id)
            
            serializer = SolicitudesViajeUsuarioResponseSerializer(data=resultado)
            
            if not serializer.is_valid():
                logger.error(f"Error de serialización: {serializer.errors}")
                return Response(
                    {
                        'error': 'Error al procesar los datos',
                        'detalle': serializer.errors
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            logger.info(f"Solicitudes de viaje encontradas: {resultado['total']}")
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.exception(f"Error al obtener solicitudes de viaje: {str(e)}")
            return Response(
                {
                    'error': 'Error al obtener solicitudes de viaje',
                    'detalle': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @classmethod
    def as_service(cls, usuario_id: int) -> dict:
        """Método para usar el endpoint como servicio interno."""
        service = SolicitudesViajeUsuarioService()
        return service.obtener_solicitudes_usuario(usuario_id)