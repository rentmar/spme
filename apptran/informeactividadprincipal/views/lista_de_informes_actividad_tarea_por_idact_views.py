# views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from spme_actividades.models import Actividad
from ..serializers.lista_de_informes_actividad_tarea_por_idact_serializer import ActividadDetalladaSerializer

class ActividadDetalladaView(generics.RetrieveAPIView):
    """
    Endpoint para obtener una actividad por ID con todas sus relaciones:
    - Informes directos de la actividad
    - Tareas relacionadas
    - Informes de cada tarea
    """
    # permission_classes = [IsAuthenticated]
    serializer_class = ActividadDetalladaSerializer
    
    def get_object(self):
        actividad_id = self.kwargs.get('actividad_id')
        # Puedes agregar lógica adicional para filtrar por usuario/proyecto si es necesario
        actividad = get_object_or_404(
            Actividad.objects.prefetch_related(
                'tareas',
                'actividad_informes_de_actividad_principal',
                'tareas__tarea_informes_de_subactividad_principal'
            ),
            id=actividad_id,
            estaInactiva=False  # Excluir actividades inactivas si lo deseas
        )
        return actividad
    
    def get(self, request, *args, **kwargs):
        try:
            actividad = self.get_object()
            serializer = self.get_serializer(actividad)
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Actividad.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Actividad no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)