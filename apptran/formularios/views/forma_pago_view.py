# spme/apptran/formularios/views/forma_pago_view.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import logging

from ..repositories.forma_pago_repository import FormaPagoRepository
from ..services.forma_pago_service import FormaPagoService
from ..serializers.forma_pago_serializer import BeneficiariosAgrupadosSerializer

logger = logging.getLogger(__name__)

class BeneficiariosFormaPagoView(APIView):
    """
    Vista para obtener beneficiarios agrupados por tipo de forma de pago.
    
    Endpoint: GET /beneficiarios-forma-pago/
    
    Response:
    {
        "efectivo": [...],
        "transferencia": [...],
        "cheque": [...],
        "todos": [...]
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repository = FormaPagoRepository()
        self.service = FormaPagoService(self.repository)
    
    def get(self, request):
        try:
            datos = self.service.obtener_beneficiarios_agrupados()
            serializer = BeneficiariosAgrupadosSerializer(datos)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error en BeneficiariosFormaPagoView: {str(e)}")
            return Response(
                {
                    'error': 'Error al procesar la solicitud',
                    'detail': str(e) if settings.DEBUG else 'Error interno del servidor'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )