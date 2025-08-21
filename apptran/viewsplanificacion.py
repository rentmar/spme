# views.py (continuación)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from spme_planificacion.models import PlanificacionProyecto
from .serializerplanificacion import HistorialPlanificacionSerializer
from rest_framework import status
from django.db.models import Count, Q
from django.utils import timezone


@api_view(['GET'])
def obtener_historial_planificacion(request, idproyecto):
    """
    Obtiene el historial de planificaciones de un proyecto
    GET /actividades/historial-planificacion/<idproyecto>/
    """
    try:
        planificaciones = PlanificacionProyecto.objects.filter(
            proyecto_id=idproyecto
        ).prefetch_related('cambios').order_by('-version')
        
        serializer = HistorialPlanificacionSerializer(planificaciones, many=True)
        return Response(serializer.data)
    
    except Exception as e:
        return Response(
            {'error': f'Error al obtener historial: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def obtener_planificacion_version(request, idproyecto, version):
    """
    Obtiene una versión específica de planificación
    GET /actividades/planificacion/<idproyecto>/<version>/
    """
    try:
        planificacion = PlanificacionProyecto.objects.get(
            proyecto_id=idproyecto,
            version=version
        )
        
        # Devolver los datos completos de la planificación
        return Response({
            'id': planificacion.id,
            'proyecto': planificacion.proyecto_id,
            'version': planificacion.version,
            'table_config': planificacion.table_config,
            'rows_data': planificacion.rows_data,
            'creado': planificacion.creado,
            'creado_por': planificacion.creado_por
        })
    
    except PlanificacionProyecto.DoesNotExist:
        return Response(
            {'error': 'Planificación no encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Error al obtener planificación: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['GET'])
def contar_planificaciones(request):
    """
    Endpoint para obtener la cantidad de registros en PlanificacionProyecto
    GET /api/planificaciones/contar/
    
    Parámetros opcionales:
    - proyecto_id: Filtrar por proyecto específico
    - version: Filtrar por versión específica
    """
    try:
        # Obtener parámetros de query string
        proyecto_id = request.GET.get('proyecto_id')
        version = request.GET.get('version')
        
        # Construir el queryset base
        queryset = PlanificacionProyecto.objects.all()
        
        # Aplicar filtros si se proporcionan
        if proyecto_id:
            queryset = queryset.filter(proyecto_id=proyecto_id)
        
        if version:
            queryset = queryset.filter(version=version)
        
        # Obtener el conteo total
        total_registros = queryset.count()
        
        # Opcional: Conteo adicional por proyecto si se solicita
        conteo_por_proyecto = {}
        if request.GET.get('agrupar_por_proyecto'):
            conteo_por_proyecto = queryset.values('proyecto__id', 'proyecto__nombre').annotate(
                total=Count('id')
            )
        
        # Preparar respuesta
        response_data = {
            'total_registros': total_registros,
            'filtros_aplicados': {
                'proyecto_id': proyecto_id,
                'version': version
            }
        }
        
        # Agregar conteo por proyecto si se solicitó
        if conteo_por_proyecto:
            response_data['conteo_por_proyecto'] = list(conteo_por_proyecto)
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error al contar planificaciones: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )    
    

# # views.py (versión alternativa)
# @api_view(['GET'])
# def estadisticas_planificaciones(request):
#     """
#     Endpoint para obtener estadísticas detalladas de PlanificacionProyecto
#     GET /api/planificaciones/estadisticas/
#     """
#     try:
#         # Conteo total
#         total_registros = PlanificacionProyecto.objects.count()
        
#         # Conteo por proyecto
#         por_proyecto = PlanificacionProyecto.objects.values(
#             'proyecto__id', 'proyecto__nombre'
#         ).annotate(
#             total=Count('id'),
#             ultima_version=Max('version'),
#             primera_fecha=Min('creado'),
#             ultima_fecha=Max('creado')
#         ).order_by('proyecto__nombre')
        
#         # Proyecto con más planificaciones
#         proyecto_mas_planificaciones = PlanificacionProyecto.objects.values(
#             'proyecto__id', 'proyecto__nombre'
#         ).annotate(
#             total=Count('id')
#         ).order_by('-total').first()
        
#         # Rango de fechas
#         fecha_mas_antigua = PlanificacionProyecto.objects.aggregate(
#             Min('creado')
#         )['creado__min']
        
#         fecha_mas_reciente = PlanificacionProyecto.objects.aggregate(
#             Max('creado')
#         )['creado__max']
        
#         # Versión más alta
#         version_maxima = PlanificacionProyecto.objects.aggregate(
#             Max('version')
#         )['version__max']
        
#         response_data = {
#             'total_registros': total_registros,
#             'por_proyecto': list(por_proyecto),
#             'proyecto_mas_planificaciones': proyecto_mas_planificaciones,
#             'rango_fechas': {
#                 'desde': fecha_mas_antigua,
#                 'hasta': fecha_mas_reciente
#             },
#             'version_maxima': version_maxima,
#             'actualizado': timezone.now().isoformat()
#         }
        
#         return Response(response_data, status=status.HTTP_200_OK)
        
#     except Exception as e:
#         return Response(
#             {'error': f'Error al obtener estadísticas: {str(e)}'},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )    