# modules/presupuesto/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..services.presupuesto_tree_service import PresupuestoTreeService
import logging

logger = logging.getLogger(__name__)

class EstructuraPresupuestoView(APIView):
    """
    Endpoint para obtener la estructura del presupuesto.
    GET /api/proyectos/{proyecto_id}/estructura-presupuesto/
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = PresupuestoTreeService()
    
    def get(self, request, proyecto_id):
        try:
            estructura = self.service.obtener_estructura_presupuesto(proyecto_id)
            return Response(estructura, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error en vista: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )