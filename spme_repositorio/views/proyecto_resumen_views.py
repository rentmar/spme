# spme/spme_repositorio/views/proyecto_resumen_views.py
import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from spme_repositorio.services.proyecto_resumen.proyecto_resumen_service import (
    ProyectoResumenService,
)
from spme_repositorio.serializers.proyecto_resumen_serializers import (
    ProyectoResumenSerializer,
)

logger = logging.getLogger(__name__)


class ProyectosResumenView(APIView):
    """
    Endpoint para obtener el resumen de repositorio de todos los proyectos.
    
    GET /api-repo/repositorio/proyectos-resumen/
    """

    def get(self, request, *args, **kwargs):
        try:
            service = ProyectoResumenService()
            resumen = service.generar_resumen_completo()

            # Validar con serializer
            serializer = ProyectoResumenSerializer(resumen, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error generando resumen de proyectos: {e}")
            return Response(
                {'error': f'Error interno: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )