# spme/apptran/proyecto/views/actividad_views.py
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from ..services.actividad_service import ActividadService
from ..serializers.actividad_serializer import ActividadSerializer 


class ActividadViewSet(ViewSet):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ActividadService()

    @action(detail=True, methods=['get'])
    def detalle(self, request, pk=None):
        """
        GET /api/actividades/{id}/detalle/
        """
        try:
            actividad = self.service.obtener_actividad(pk)
            serializer = ActividadSerializer(actividad)
            return Response(serializer.data)

        except Exception as e:
            return Response({'error': str(e)}, status=404)

