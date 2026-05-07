from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from spme_estructuracion_proyecto.models import Proyecto
from ..serializers.lista_proyectos_habilitados_serializer import (
    ProyectoHabilitadoSerializer,
    ProyectoResumenSerializer,
)


class ProyectoHabilitadoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet con 3 endpoints para proyectos habilitados"""
    queryset = Proyecto.objects.filter(esta_habilitado=True)
    
    def get_serializer_class(self):
        """Selecciona el serializador según el endpoint"""
        if self.action == 'resumen':
            return ProyectoResumenSerializer
        return ProyectoHabilitadoSerializer
    
    # Endpoint 1: Información completa
    def list(self, request, *args, **kwargs):
        """
        GET /api/proyectos/habilitados/
        Devuelve información completa de proyectos habilitados
        """
        queryset = self.get_queryset()
        serializer = ProyectoHabilitadoSerializer(queryset, many=True)
        return Response({
            'proyectos': serializer.data,
            'total': queryset.count()
        })
    
    # Endpoint 2: Solo IDs
    @action(detail=False, methods=['get'], url_path='solo-ids')
    def solo_ids(self, request):
        """
        GET /api/proyectos/habilitados/solo-ids/
        Devuelve solo los IDs de proyectos habilitados
        """
        ids = list(self.get_queryset().values_list('id', flat=True))
        return Response({
            'ids': ids,
            'total': len(ids)
        })
    
    # Endpoint 3: Información resumida
    @action(detail=False, methods=['get'], url_path='resumen')
    def resumen(self, request):
        """
        GET /api/proyectos/habilitados/resumen/
        Devuelve información resumida de proyectos habilitados
        """
        queryset = self.get_queryset()
        serializer = ProyectoResumenSerializer(queryset, many=True)
        return Response({
            'proyectos': serializer.data,
            'total': queryset.count()
        })