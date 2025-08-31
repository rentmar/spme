# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from spme_actividades.models import Actividad
from spme_estructuracion_proyecto.models import Proyecto
#from .models import Actividad, Proyecto
#from .serializers import ActividadProyectoSerializer
from .serializeractividad import ActividadProyectoSerializer

@api_view(['GET'])
def actividades_por_proyecto(request, proyecto_id):
    """
    Obtiene todas las actividades de un proyecto específico.
    GET actividades/proyecto/<idproyecto>/
    """
    try:
        # Verificar que el proyecto existe
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)
        
        # Obtener actividades del proyecto
        actividades = Actividad.objects.filter(proyecto_id=proyecto_id)
        
        # Aplicar filtros adicionales si existen
        estado = request.query_params.get('estado')
        if estado:
            actividades = actividades.filter(estado=estado)
            
        # Filtrar por tipo (usando la sigla)
        tipo_filter = request.query_params.get('tipo')
        if tipo_filter:
            actividades = actividades.filter(tipo__sigla=tipo_filter)
        
        # Filtrar por responsable (username)
        responsable_filter = request.query_params.get('responsable')
        if responsable_filter:
            actividades = actividades.filter(responsable__username=responsable_filter)
        
        # Serializar los datos
        serializer = ActividadProyectoSerializer(actividades, many=True)
        
        # Response con el formato solicitado
        response_data = {
            'proyecto': {
                'id': proyecto.id,
                'nombre': proyecto.titulo,
                'codigo': proyecto.codigo
            },
            'actividades': serializer.data,
            'total': actividades.count()
        }
        
        return Response(response_data)
        
    except ValueError:
        return Response(
            {'error': 'ID de proyecto inválido'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Proyecto.DoesNotExist:
        return Response(
            {'error': f'Proyecto con ID {proyecto_id} no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )