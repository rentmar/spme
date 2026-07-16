# views/solicitudes_reembolso_usuario_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import logging

from ..services.solicitudes_reembolso_usuario_service import (
    SolicitudesReembolsoUsuarioService
)
from ..serializers.solicitudes_reembolso_usuario_serializers import (
    SolicitudesReembolsoUsuarioResponseSerializer
)

logger = logging.getLogger(__name__)


class SolicitudesReembolsoUsuarioView(APIView):
    """
    Endpoint especializado para obtener solicitudes de reembolso del usuario.
    
    GET /api-valid/mis-solicitudes-reembolso/
    
    Headers requeridos:
        Authorization: Bearer <token>
    
    Respuesta exitosa (200):
        {
            "tipo": "solicitudes_reembolso",
            "total": 1,
            "solicitudes": [...],
            "resumen": {...}
        }
    
    Características:
    1. Funciona independientemente
    2. Diseñado para ser reutilizado por un endpoint maestro
    3. Incluye método as_service() para consumo interno
    
    Errores:
        401: Usuario no autenticado
        500: Error interno del servidor
    """
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, service=None, **kwargs):
        """
        Constructor que permite inyección del servicio para testing.
        
        Args:
            service: Instancia del servicio (opcional, para tests)
        """
        super().__init__(**kwargs)
        self.service = service or SolicitudesReembolsoUsuarioService()
    
    def get(self, request):
        """
        Maneja peticiones GET para obtener solicitudes de reembolso del usuario.
        
        Args:
            request: Objeto HttpRequest con datos del usuario autenticado
            
        Returns:
            Response con datos estructurados o error
        """
        try:
            usuario_id = request.user.id
            
            logger.info(f"Obteniendo solicitudes de reembolso para usuario ID={usuario_id}")
            
            resultado = self.service.obtener_solicitudes_usuario(usuario_id)
            
            serializer = SolicitudesReembolsoUsuarioResponseSerializer(data=resultado)
            
            if not serializer.is_valid():
                logger.error(f"Error de serialización: {serializer.errors}")
                return Response(
                    {
                        'error': 'Error al procesar los datos',
                        'detalle': serializer.errors
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            logger.info(f"Solicitudes de reembolso encontradas: {resultado['total']}")
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.exception(f"Error al obtener solicitudes de reembolso: {str(e)}")
            return Response(
                {
                    'error': 'Error al obtener solicitudes de reembolso',
                    'detalle': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @classmethod
    def as_service(cls, usuario_id: int) -> dict:
        """
        Método de clase para usar el endpoint como servicio interno.
        
        Permite que otros endpoints (como un endpoint maestro) consuman
        este endpoint directamente sin hacer peticiones HTTP.
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Diccionario con solicitudes de reembolso
            
        Ejemplo de uso desde otro endpoint:
            reembolsos = SolicitudesReembolsoUsuarioView.as_service(usuario_id)
        """
        service = SolicitudesReembolsoUsuarioService()
        return service.obtener_solicitudes_usuario(usuario_id)