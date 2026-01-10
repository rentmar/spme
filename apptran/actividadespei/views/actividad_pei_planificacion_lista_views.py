# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from spme_estructuracion_pei.models import ActividadPei
from spme_estructuracion_pei.models import Pei
from ..serializers.actividad_pei_planificacion_lista_serializer import ActividadPeiListaPlanificacion

@api_view(['GET'])
def actividades_por_pei_planificacion(request, pei_id):
    """
    Obtiene todas las actividades de un pei específico.
    Con el formato para la planificacion
    GET actividades/pei/<idpei>/
    """
    try:
        # Verificar que el proyecto existe
        pei = get_object_or_404(Pei, id=pei_id)
        
        # Obtener actividades del proyecto
        actividades = ActividadPei.objects.filter(pei_id=pei_id)
        
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
        serializer = ActividadPeiListaPlanificacion(actividades, many=True)
        
        # Response con el formato solicitado
        response_data = {
            'pei': {
                'id': pei.id,
                'titulo': pei.titulo,
                'descripcion': pei.descripcion
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
    except Pei.DoesNotExist:
        return Response(
            {'error': f'Proyecto con ID {pei_id} no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

