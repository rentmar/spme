# views.py
from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models import CambioPlanificacion, PlanificacionProyecto
from ..serializers.cambio_plan_idplan_serializers import CambioPlanificacionSerializer
#from .models import CambioPlanificacion, PlanificacionProyecto
#from .serializers import CambioPlanificacionSerializer

class CambiosPlanificacionListView(generics.ListAPIView):
    """
    Endpoint para obtener todos los cambios de una planificación específica
    """
    serializer_class = CambioPlanificacionSerializer
    
    def get_queryset(self):
        """
        Filtra los cambios por el ID de planificación proporcionado en la URL
        """
        planificacion_id = self.kwargs['planificacion_id']
        
        # Verificar que la planificación existe
        planificacion = get_object_or_404(PlanificacionProyecto, id=planificacion_id)
        
        # Retornar los cambios ordenados por fecha descendente
        return CambioPlanificacion.objects.filter(
            planificacion_id=planificacion_id
        ).order_by('-realizado_el')
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            
            # Incluir información adicional en la respuesta
            planificacion_id = self.kwargs['planificacion_id']
            response_data = {
                'success': True,
                'planificacion_id': planificacion_id,
                'total_cambios': queryset.count(),
                'cambios': serializer.data
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'message': 'Error al obtener los cambios de la planificación'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

