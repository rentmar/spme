# views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from spme_monitoreo.models import InfTarea
from ..serializers.informe_tarea_serializer import InfTareaSerializer


# views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from spme_monitoreo.models import InfTarea
from ..serializers.informe_tarea_serializer import InfTareaSerializer

@api_view(['POST'])
def crear_informe_tarea(request):
    """
    Endpoint para GUARDAR un nuevo informe de tarea
    POST /api/informes-tarea/crear/
    """
    if request.method == 'POST':
        serializer = InfTareaSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                informe = serializer.save()
                return Response({
                    'id': informe.id,
                    'numeroInforme': informe.numeroInforme,
                    'mensaje': 'Informe guardado correctamente'
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {'error': f'Error al guardar el informe: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def listar_informes_tarea(request):
    """
    Endpoint para EXTRAER/OBTENER informes de tarea
    GET /api/informes-tarea/listar/
    GET /api/informes-tarea/listar/?tarea_id=5
    GET /api/informes-tarea/listar/?actividad_id=22
    """
    if request.method == 'GET':
        try:
            # Obtener parámetros de filtro
            tarea_id = request.GET.get('tarea_id')
            actividad_id = request.GET.get('actividad_id')
            
            # Construir queryset base
            informes = InfTarea.objects.all().select_related(
                'tarea', 'tarea__actividad'
            ).order_by('-created_at')
            
            # Aplicar filtros
            if tarea_id:
                informes = informes.filter(tarea__id=tarea_id)
            
            if actividad_id:
                informes = informes.filter(tarea__actividad__id=actividad_id)
            
            serializer = InfTareaSerializer(informes, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener informes: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

@api_view(['GET'])
def obtener_informe_tarea(request, informe_id):
    """
    Endpoint para EXTRAER/OBTENER un informe específico
    GET /api/informes-tarea/obtener/1/
    """
    if request.method == 'GET':
        try:
            informe = InfTarea.objects.get(id=informe_id)
            serializer = InfTareaSerializer(informe)
            return Response(serializer.data)
            
        except InfTarea.DoesNotExist:
            return Response(
                {'error': 'El informe no existe'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al obtener el informe: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

@api_view(['PUT'])
def actualizar_informe_tarea(request, informe_id):
    """
    Endpoint para ACTUALIZAR un informe existente
    PUT /api/informes-tarea/actualizar/1/
    """
    if request.method == 'PUT':
        try:
            informe = InfTarea.objects.get(id=informe_id)
            serializer = InfTareaSerializer(informe, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'mensaje': 'Informe actualizado correctamente',
                    'data': serializer.data
                })
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except InfTarea.DoesNotExist:
            return Response(
                {'error': 'El informe no existe'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al actualizar el informe: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

@api_view(['DELETE'])
def eliminar_informe_tarea(request, informe_id):
    """
    Endpoint para ELIMINAR un informe existente
    DELETE /api/informes-tarea/eliminar/1/
    """
    if request.method == 'DELETE':
        try:
            informe = InfTarea.objects.get(id=informe_id)
            numero_informe = informe.numeroInforme
            informe.delete()
            
            return Response({
                'mensaje': f'Informe {numero_informe} eliminado correctamente',
                'numeroInforme': numero_informe,
                'id_eliminado': informe_id
            }, status=status.HTTP_200_OK)
            
        except InfTarea.DoesNotExist:
            return Response(
                {'error': 'El informe no existe'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al eliminar el informe: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )