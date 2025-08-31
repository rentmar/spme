# views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from spme_monitoreo.models import SolicitudViaje
from ..serializers.serializercrearsolicitudviaje import SolicitudViajeCreateSerializer

class SolicitudViajeCreateView(generics.CreateAPIView):
    queryset = SolicitudViaje.objects.all()
    serializer_class = SolicitudViajeCreateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        # Respuesta personalizada
        response_data = {
            "success": True,
            "message": "Solicitud de fondos creada exitosamente",
            "id": instance.id,
            "numero_formulario": instance.numeroFormulario
        }
        
        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

# Versión con función basada en vista
@api_view(['POST'])
def crear_solicitud_viaje(request):
    serializer = SolicitudViajeCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        instance = serializer.save()
        
        response_data = {
            "success": True,
            "message": "Solicitud de fondos creada exitosamente",
            "id": instance.id,
            "numero_formulario": instance.numeroFormulario
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    # En caso de error
    return Response({
        "success": False,
        "message": "Error al crear la solicitud",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)