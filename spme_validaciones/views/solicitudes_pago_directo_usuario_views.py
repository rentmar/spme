# views/solicitudes_pago_directo_usuario_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import logging

from ..services.solicitudes_pago_directo_usuario_service import (
    SolicitudesPagoDirectoUsuarioService
)
from ..serializers.solicitudes_pago_directo_usuario_serializers import (
    SolicitudesPagoDirectoUsuarioResponseSerializer
)

logger = logging.getLogger(__name__)


class SolicitudesPagoDirectoUsuarioView(APIView):
    """
    Endpoint especializado para obtener solicitudes de pago directo del usuario.
    
    GET /api-valid/mis-solicitudes-pago-directo/
    """
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, service=None, **kwargs):
        super().__init__(**kwargs)
        self.service = service or SolicitudesPagoDirectoUsuarioService()
    
    def get(self, request):
        try:
            usuario_id = request.user.id
            
            logger.info(f"Obteniendo solicitudes de pago directo para usuario ID={usuario_id}")
            
            resultado = self.service.obtener_solicitudes_usuario(usuario_id)
            
            serializer = SolicitudesPagoDirectoUsuarioResponseSerializer(data=resultado)
            
            if not serializer.is_valid():
                logger.error(f"Error de serialización: {serializer.errors}")
                return Response(
                    {
                        'error': 'Error al procesar los datos',
                        'detalle': serializer.errors
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            logger.info(f"Solicitudes de pago directo encontradas: {resultado['total']}")
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.exception(f"Error al obtener solicitudes de pago directo: {str(e)}")
            return Response(
                {
                    'error': 'Error al obtener solicitudes de pago directo',
                    'detalle': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @classmethod
    def as_service(cls, usuario_id: int) -> dict:
        """Método para usar el endpoint como servicio interno."""
        service = SolicitudesPagoDirectoUsuarioService()
        return service.obtener_solicitudes_usuario(usuario_id)