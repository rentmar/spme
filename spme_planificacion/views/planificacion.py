from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
# from .orquestador import guardar_planificacion as orquestar
from ..services.orquestador import guardar_planificacion as orquestar


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def guardar_planificacion(request):
    """Endpoint transaccional. Delega toda la lógica al orquestador."""
    try:
        resultado = orquestar(request.data, request.user.id)
        return Response(resultado, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)