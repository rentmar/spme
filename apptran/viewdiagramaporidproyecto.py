from rest_framework import generics, status
from rest_framework.response import Response
from spme_estructuracion_proyecto.models import DiagramaEstructura
from .serializerdiagramaporidproyecto import DiagramaEstructuraSerializer

class DiagramaPorProyectoView(generics.RetrieveAPIView):
    """
    Endpoint para obtener un diagrama de estructura por ID de proyecto
    """
    serializer_class = DiagramaEstructuraSerializer
    
    def get_object(self):
        proyecto_id = self.kwargs.get('proyecto_id')
        try:
            return DiagramaEstructura.objects.get(proyecto_id=proyecto_id)
        except DiagramaEstructura.DoesNotExist:
            return None
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response(
                {"error": "No se encontró un diagrama para este proyecto"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)