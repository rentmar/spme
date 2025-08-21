# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
# from .models import Actividad
# from .serializers import ActividadBulkSerializer
from spme_actividades.models import Actividad
from .serializeractividadbulk import ActividadBulkSerializer


@api_view(['POST'])
@transaction.atomic
def procesar_actividades_bulk(request):
    """
    Procesa un array de actividades (crear o actualizar)
    POST /actividades/procesar-bulk/
    """
    try:
        actividades_data = request.data
        
        if not isinstance(actividades_data, list):
            return Response(
                {'error': 'Se esperaba un array de actividades'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resultados = {
            'creadas': 0,
            'actualizadas': 0,
            'errores': [],
            'detalles': []
        }
        
        for index, actividad_data in enumerate(actividades_data):
            try:
                # Determinar si es creación o actualización
                actividad_id = actividad_data.get('id', 0)
                
                if actividad_id == 0:
                    # Crear nueva actividad
                    serializer = ActividadBulkSerializer(data=actividad_data)
                    if serializer.is_valid():
                        actividad = serializer.save()
                        resultados['creadas'] += 1
                        resultados['detalles'].append({
                            'index': index,
                            'id': actividad.id,
                            'accion': 'creada',
                            'estado': 'éxito'
                        })
                    else:
                        resultados['errores'].append({
                            'index': index,
                            'error': serializer.errors,
                            'accion': 'crear'
                        })
                
                else:
                    # Actualizar actividad existente
                    try:
                        actividad = Actividad.objects.get(id=actividad_id)
                        serializer = ActividadBulkSerializer(actividad, data=actividad_data, partial=True)
                        if serializer.is_valid():
                            serializer.save()
                            resultados['actualizadas'] += 1
                            resultados['detalles'].append({
                                'index': index,
                                'id': actividad_id,
                                'accion': 'actualizada',
                                'estado': 'éxito'
                            })
                        else:
                            resultados['errores'].append({
                                'index': index,
                                'id': actividad_id,
                                'error': serializer.errors,
                                'accion': 'actualizar'
                            })
                    except Actividad.DoesNotExist:
                        resultados['errores'].append({
                            'index': index,
                            'id': actividad_id,
                            'error': 'Actividad no encontrada',
                            'accion': 'actualizar'
                        })
            
            except Exception as e:
                resultados['errores'].append({
                    'index': index,
                    'id': actividad_data.get('id', 'desconocido'),
                    'error': str(e),
                    'accion': 'procesar'
                })
        
        # Response final
        return Response(resultados, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )