#spme/spme_presupuesto/views/ejecucion_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

#Modelos
from spme_actividades.models import Actividad, TareaActividad

#Servicio
from spme_presupuesto.services.ejecucion_service import EjecucionService

#Serializador
from ..serializers.balance_serializers import (
    ActividadEjecutadaSerializer,
    TareaEjecucionDetalleSerializer,
)


class EjecucionActividadView(APIView):
    """
    Detalle de ejecucion de una actividad
    """
    def get(self, request, actividad_id):
        try:
            service = EjecucionService()
            datos = service.detalle_ejecucion_actividad(actividad_id)
            serializer = ActividadEjecutadaSerializer(datos)
            return Response(serializer.data)
        except Actividad.DoesNotExist:
            return Response(
                {'error': 'Actividad no encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
class EjecucionTareaView(APIView):
    """
    Detalle de ejecución de una tarea
    """
    def get(self, request, tarea_id):
        try:
            service = EjecucionService()
            datos = service.detalle_ejecucion_tarea(tarea_id)
            serializer = TareaEjecucionDetalleSerializer(datos)
            return Response(serializer.data)
        except TareaActividad.DoesNotExist:
            return Response(
                {'error': 'Tarea no encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
