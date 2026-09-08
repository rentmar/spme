# spme/spme_fonfosc/views/institucion_crud_basico_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from spme_fonfosc.services.institucion_service import InstitucionService


class InstitucionListView(APIView):
    """Vista para listar instituciones"""

    def get(self, request):
        instituciones = InstitucionService.listar_instituciones()
        return Response(instituciones, status=status.HTTP_200_OK)


class InstitucionDetailView(APIView):
    """Vista para obtener una institución por ID"""

    def get(self, request, institucion_id):
        institucion = InstitucionService.obtener_institucion(institucion_id)
        if not institucion:
            return Response(
                {'detail': 'Institución no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(institucion, status=status.HTTP_200_OK)