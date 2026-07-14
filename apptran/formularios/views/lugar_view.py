# spme/apptran/formularios/views/lugar_view.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import logging

from ..repositories.lugar_repository import LugarRepository
from ..services.lugar_service import LugarService
from ..serializers.lugar_serializer import LugaresAgrupadosSerializer

logger = logging.getLogger(__name__)

class LugaresSolicitudView(APIView):
    """
    Vista para obtener lugares de solicitud de todos los formularios.
    
    Endpoint: GET /api/lugares-solicitud/
    
    Response:
    {
        "lugares_unicos": ["Alemania", "Cochabamba", "La Paz", ...],
        "lugares_por_tipo": {
            "Solicitud de Fondos": ["La Paz", "Santa Cruz"],
            "Solicitud de Viaje": ["Paris", "Alemania"],
            ...
        },
        "lugares_con_estadisticas": [
            {
                "nombre": "La Paz",
                "cantidad_registros": 15,
                "tipos_formulario": ["Solicitud de Fondos", "Solicitud de Viaje"]
            },
            ...
        ],
        "total_lugares_unicos": 5,
        "total_registros": 25
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repository = LugarRepository()
        self.service = LugarService(self.repository)
    
    def get(self, request):
        try:
            datos = self.service.obtener_lugares_agrupados()
            serializer = LugaresAgrupadosSerializer(datos)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error en LugaresSolicitudView: {str(e)}")
            return Response(
                {
                    'error': 'Error al procesar la solicitud',
                    'detail': str(e) if settings.DEBUG else 'Error interno del servidor'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )