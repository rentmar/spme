# views.py
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from spme_monitoreo.models import SolicitudViaje
from ..serializers.serializaerobtenersolicitudviaje import SolicitudViajeSerializer

class SolicitudViajeListView(generics.ListAPIView):
    queryset = SolicitudViaje.objects.all()
    serializer_class = SolicitudViajeSerializer

class SolicitudViajeDetailView(generics.RetrieveAPIView):
    queryset = SolicitudViaje.objects.all()
    serializer_class = SolicitudViajeSerializer

# Opcional: Si quieres un endpoint que devuelva todas las solicitudes
@api_view(['GET'])
def solicitud_viaje_list(request):
    solicitudes = SolicitudViaje.objects.all()
    serializer = SolicitudViajeSerializer(solicitudes, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def solicitud_viaje_detail(request, pk):
    try:
        solicitud = SolicitudViaje.objects.get(pk=pk)
        serializer = SolicitudViajeSerializer(solicitud)
        return Response(serializer.data)
    except SolicitudViaje.DoesNotExist:
        return Response({'error': 'Solicitud no encontrada'}, status=404)