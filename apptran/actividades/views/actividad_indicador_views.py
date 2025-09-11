# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from spme_actividades.models import Actividad, TareaActividad, TipoActividad
from ..serializador.actividad_indicador_serializer import ( 
    ActividadSerializer,
    TareaActividadSerializer, 
    TipoActividadSerializer
    )


class TipoActividadViewSet(viewsets.ModelViewSet):
    queryset = TipoActividad.objects.all()
    serializer_class = TipoActividadSerializer

class ActividadIndicadorViewSet(viewsets.ModelViewSet):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        actividad = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        if nuevo_estado not in dict(Actividad.ESTADOS_ACTIVIDAD).keys():
            return Response(
                {'error': 'Estado no válido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        actividad.estado = nuevo_estado
        actividad.save()
        
        return Response({
            'message': f'Estado cambiado a {nuevo_estado}',
            'actividad': ActividadSerializer(actividad).data
        })

    @action(detail=True, methods=['post'])
    def anular(self, request, pk=None):
        actividad = self.get_object()
        actividad.estaInactiva = True
        actividad.save()
        
        return Response({
            'message': 'Actividad anulada',
            'actividad': ActividadSerializer(actividad).data
        })

    @action(detail=True, methods=['get'])
    def tareas(self, request, pk=None):
        actividad = self.get_object()
        tareas = actividad.tareas.all()
        serializer = TareaActividadSerializer(tareas, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def agregar_tarea(self, request, pk=None):
        actividad = self.get_object()
        serializer = TareaActividadSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(actividad=actividad)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TareaActividadViewSet(viewsets.ModelViewSet):
    queryset = TareaActividad.objects.all()
    serializer_class = TareaActividadSerializer

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        tarea = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        if nuevo_estado not in dict(TareaActividad.ESTADOS_TAREA).keys():
            return Response(
                {'error': 'Estado no válido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tarea.estado = nuevo_estado
        tarea.save()
        
        return Response({
            'message': f'Estado cambiado a {nuevo_estado}',
            'tarea': TareaActividadSerializer(tarea).data
        })