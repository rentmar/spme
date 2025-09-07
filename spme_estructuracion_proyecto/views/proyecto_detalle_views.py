# views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from spme_estructuracion_proyecto.models import Proyecto, ProcedenciaFondos, InstanciaGestora
from spme_estructuracion_pei.models import Pei
from ..serializers.proyecto_detalle_serializers import ProyectoDetailSerializer

class ProyectoDetailView(generics.RetrieveAPIView):
    """
    Endpoint para obtener toda la información de un proyecto específico usando su id
    """
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoDetailSerializer
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        try:
            proyecto = self.get_object()
            serializer = self.get_serializer(proyecto)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Proyecto.DoesNotExist:
            return Response(
                {"error": "Proyecto no encontrado"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        

@api_view(['GET'])
def test_connection(request):
    """
    Endpoint de prueba para verificar la conexión con el API
    """
    return Response({"message": "CONEXION CORRECTA"}, status=status.HTTP_200_OK)        