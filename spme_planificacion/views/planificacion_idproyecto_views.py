# views.py (alternativa)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.planificacion_idproyecto_serializers import PlanificacionProyectoSerializer
from spme_planificacion.models import PlanificacionProyecto
# from .models import PlanificacionProyecto
# from .serializers import PlanificacionProyectoSerializer

class PlanificacionesPorProyectoAPIView(APIView):
    """
    APIView específica para obtener planificaciones por proyecto
    """
    
    def get(self, request, proyecto_id):
        """
        GET /api/planificaciones/proyecto/<proyecto_id>/
        """
        try:
            # Validar que el proyecto_id sea un número válido
            proyecto_id_int = int(proyecto_id)
            
            planificaciones = PlanificacionProyecto.objects.filter(
                proyecto_id=proyecto_id_int
            ).order_by('-version')
            
            serializer = PlanificacionProyectoSerializer(planificaciones, many=True)
            
            return Response({
                'success': True,
                'proyecto_id': proyecto_id_int,
                'total_planificaciones': planificaciones.count(),
                'data': serializer.data
            })
            
        except ValueError:
            return Response({
                'success': False,
                'error': 'El ID del proyecto debe ser un número válido'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al obtener las planificaciones: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

