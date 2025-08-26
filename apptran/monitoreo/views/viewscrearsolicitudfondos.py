# views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from spme_monitoreo.models import SolicitudFondos
from ..serializers.serializercrearsolicitudfondos import SolicitudFondosCreateSerializer
#from .models import SolicitudFondos
#from .serializers import SolicitudFondosCreateSerializer

@api_view(['POST'])
@permission_classes([AllowAny])  # Permite acceso sin autenticación
def crear_solicitud_fondos(request):
    """
    Endpoint POST para crear una nueva solicitud de fondos
    """
    serializer = SolicitudFondosCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            solicitud = serializer.save()
            return Response(
                {
                    'success': True,
                    'message': 'Solicitud de fondos creada exitosamente',
                    'id': solicitud.id,
                    'numero_formulario': solicitud.numeroFormulario
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': f'Error al crear la solicitud: {str(e)}'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response(
        {
            'success': False,
            'message': 'Datos inválidos',
            'errors': serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST
    )