# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from spme_actividades.models import Actividad, TareaActividad
from spme_autenticacion.models import Usuario
from ..serializador.lista_actividad_tarea_serializer import ActividadConTareasSerializer

# from .models import Actividad, TareaActividad, Usuario
# from .serializers import ActividadConTareasSerializer

class ActividadSubActividadViewSet(viewsets.ModelViewSet):
    queryset = Actividad.objects.all()
    serializer_class = ActividadConTareasSerializer
    
    # Endpoint 1: Actividades por username del responsable
    @action(detail=False, methods=['get'], url_path='por-responsable/(?P<username>[^/.]+)')
    def actividades_por_responsable(self, request, username=None):
        try:
            # Verificar si el usuario existe
            usuario = get_object_or_404(Usuario, username=username)
            
            # Obtener actividades donde el responsable coincide con el username
            actividades = Actividad.objects.filter(
                responsable__username=username
            ).prefetch_related('tareas')
            
            serializer = self.get_serializer(actividades, many=True)
            return Response({
                'username': username,
                'nombre_responsable': usuario.get_full_name(),
                'cantidad_actividades': actividades.count(),
                'actividades': serializer.data
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener actividades: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # Endpoint 2: Todas las actividades con sus tareas
    @action(detail=False, methods=['get'], url_path='todas')
    def todas_actividades(self, request):
        try:
            actividades = Actividad.objects.all().prefetch_related('tareas')
            serializer = self.get_serializer(actividades, many=True)
            
            return Response({
                'cantidad_total_actividades': actividades.count(),
                'actividades': serializer.data
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener actividades: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )