# views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from spme_actividades.models import Actividad
from ..serializador.lista_informes_actividad_serializer import ActividadConTodosInformesSerializer


@api_view(['GET'])
def actividad_informes_completos(request, actividad_id):
    """
    Endpoint para obtener una actividad con TODOS sus informes 
    y TODAS sus tareas con TODOS sus informes
    """
    try:
        actividad = get_object_or_404(Actividad, id=actividad_id)
        serializer = ActividadConTodosInformesSerializer(actividad, context={'request': request})
        
        return Response(serializer.data)
        
    except Actividad.DoesNotExist:
        return Response(
            {'error': 'Actividad no encontrada'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Error al obtener los datos: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )