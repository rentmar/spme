# views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from spme_monitoreo.models import RendicionCuentas
from ..serializers.crear_rendicion_cuentas_serializer import RendicionCuentasSerializer

@api_view(['POST'])
def crear_rendicion_cuentas(request):
    """
    Endpoint para crear una nueva rendición de cuentas
    """
    try:
        # Agregar el usuario autenticado a los datos
        data = request.data.copy()
        data['usuario'] = request.user.id
        
        serializer = RendicionCuentasSerializer(data=data)
        
        if serializer.is_valid():
            rendicion = serializer.save()
            return Response({
                'message': 'Rendición de cuentas creada exitosamente',
                'data': RendicionCuentasSerializer(rendicion).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Error en los datos proporcionados',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'message': 'Error interno del servidor',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)