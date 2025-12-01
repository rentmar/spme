from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from spme_estructuracion_pei.models import ActividadPei
from ..serializers.crear_actividad_pei_serializer import ActividadPeiSerializer


@api_view(['POST'])
def crear_actividad_pei(request):
    """
    Endpoint para crear una nueva actividad PEI
    """
    try:
        serializer = ActividadPeiSerializer(data=request.data)
        
        if serializer.is_valid():
            actividad = serializer.save()
            
            return Response({
                'success': True,
                'message': 'Actividad PEI creada exitosamente',
                'actividad': ActividadPeiSerializer(actividad).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'error': 'Datos inválidos',
                'detalles': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error al crear la actividad: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT', 'PATCH'])
def actualizar_actividad_pei(request, actividad_id):
    """
    Endpoint para actualizar una actividad PEI existente
    PUT: Actualización completa
    PATCH: Actualización parcial
    """
    try:
        actividad = get_object_or_404(ActividadPei, id=actividad_id)
        
        # Determinar si es actualización parcial
        partial = request.method == 'PATCH'
        
        serializer = ActividadPeiSerializer(
            actividad, 
            data=request.data, 
            partial=partial
        )
        
        if serializer.is_valid():
            actividad_actualizada = serializer.save()
            
            return Response({
                'success': True,
                'message': 'Actividad PEI actualizada exitosamente',
                'actividad': ActividadPeiSerializer(actividad_actualizada).data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': 'Datos inválidos',
                'detalles': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except ActividadPei.DoesNotExist:
        return Response({
            'success': False,
            'error': f'Actividad con ID {actividad_id} no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error al actualizar la actividad: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)