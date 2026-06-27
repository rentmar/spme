from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

#Servicios
from ..services.balance_service import (
    BalanceService,
)

#Modelos
from spme_estructuracion_proyecto.models import Proyecto
from spme_actividades.models import Actividad, TareaActividad

#Serializadores
from ..serializers.balance_serializers import (
    BalanceProyectoSerializer,
)

class BalanceProyectoView(APIView):
    """
    Balance Completo del Proyecto
    """
    def get(self, request, proyecto_id):
        try:
            service = BalanceService()
            datos = service.balance_proyecto(proyecto_id)
            serializar = BalanceProyectoSerializer(datos)
            
            return Response(serializar.data)
        except Proyecto.DoesNotExist:
            return Response(
                {'error': 'Proyecto no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

class BalanceActividadView(APIView):
    """
    Balance de una Actvidad
    """
    def get(self, request, actividad_id):
        try:
            service = BalanceService()
            datos = service.balance_actividad(actividad_id)
            if datos:
                return Response(datos)
            return Response(
                {'error': 'Actividad no encontrada en el balance.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Actividad.DoesNotExist:
            return Response(
                {'error': 'Actividad no encontrada.'},
                    status=status.HTTP_404_NOT_FOUND
            )

class BalanceTareaView(APIView):
    """
    Balance de un tarea
    """
    def get(self, request, tarea_id):
        try:
            service = BalanceService()
            datos = service.balance_tarea(tarea_id)
            return Response(datos)
        except TareaActividad.DoesNotExist:
            return Response(
                {'error': 'Tarea no encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )