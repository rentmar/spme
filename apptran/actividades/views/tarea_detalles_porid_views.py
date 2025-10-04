# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
#from .models import TareaActividad, Actividad, TipoActividad,
from spme_actividades.models import TareaActividad
from ..serializador.tarea_detalles_porid_serializer import TareaActividadDetailSerializer


@api_view(['GET'])
def obtener_tarea_detalle(request, tarea_id):
    """
    Endpoint para obtener los detalles de una tarea específica
    incluyendo la actividad a la que pertenece y todos sus datos relacionados
    """
    try:
        # Obtener la tarea con todas las relaciones, incluyendo proyecto
        tarea = TareaActividad.objects.select_related(
            'actividad',
            'actividad__tipo',
            'actividad__proyecto',  # Incluir proyecto
            'actividad__responsable',
            'actividad__proceso',
            'actividad__resultado_og',
            'actividad__resultado_oe',
            'actividad__producto_oe',
            'actividad__objetivo_pei',
            'actividad__indicador_pei'
        ).get(id=tarea_id)
        
        # Serializar los datos
        serializer = TareaActividadDetailSerializer(tarea)
        
        return Response({
            'success': True,
            'tarea': serializer.data
        }, status=status.HTTP_200_OK)
        
    except TareaActividad.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Tarea no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error al cargar la tarea: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)