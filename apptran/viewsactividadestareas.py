from rest_framework import generics
from rest_framework.response import Response
from spme_actividades.models import Actividad
from .serializeractividadestareas import TareaActividad, ActividadSerializer

class ActividadConTareasListView(generics.ListAPIView):
    """
    Endpoint que retorna todas las actividades con sus tareas relacionadas
    """
    queryset = Actividad.objects.all().prefetch_related('tareas')
    serializer_class = ActividadSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Formatear la respuesta según el formato solicitado
        data = []
        for actividad_data in serializer.data:
            actividad_formateada = {
                'id': actividad_data['id'],
                'nombreCorto': actividad_data['nombreCorto'],
                'estado': actividad_data['estado'],
                'tareas': actividad_data['tareas']
            }
            data.append(actividad_formateada)
        
        return Response(data)

class ActividadConTareasDetailView(generics.RetrieveAPIView):
    """
    Endpoint que retorna una actividad específica con sus tareas
    """
    queryset = Actividad.objects.all().prefetch_related('tareas')
    serializer_class = ActividadSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Formatear la respuesta
        data = {
            'id': serializer.data['id'],
            'nombreCorto': serializer.data['nombreCorto'],
            'estado': serializer.data['estado'],
            'tareas': serializer.data['tareas']
        }
        
        return Response(data)