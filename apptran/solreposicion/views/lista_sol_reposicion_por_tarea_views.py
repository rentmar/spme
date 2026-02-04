from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404
from spme_monitoreo.models import SolicitudReembolso
from spme_actividades.models import Actividad, TareaActividad
from ..serializers.lista_sol_reposicion_por_tarea_serializer import SolicitudReembolsoSerializer

class SolicitudesReembolsoPorActividadYTareaView(APIView):
    """
    Endpoint para obtener solicitudes de reembolso por actividad y tarea
    """
    
    def get(self, request, id_actividad, id_tarea):
        # 1. Validar que existen
        actividad = get_object_or_404(Actividad, id=id_actividad)
        tarea = get_object_or_404(TareaActividad, id=id_tarea)
        
        # 2. Validar relación
        if tarea.actividad_id != id_actividad:
            return Response({
                'success': False,
                'error': 'La tarea no pertenece a esta actividad'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 3. Obtener queryset base
        queryset = SolicitudReembolso.objects.filter(
            actividad_id=id_actividad,
            tarea_id=id_tarea
        )
        
        # 4. Aplicar filtros
        estado = request.query_params.get('estado')
        if estado == 'pendiente':
            queryset = queryset.filter(
                validacionResponsable=False,
                validacionCoordinador=False
            )
        elif estado == 'parcial':
            queryset = queryset.filter(
                validacionResponsable=True,
                validacionCoordinador=False
            )
        elif estado == 'completo':
            queryset = queryset.filter(
                validacionResponsable=True,
                validacionCoordinador=True
            )
        
        # Ordenar
        orden = request.query_params.get('ordenar_por', '-fechaSolicitud')
        queryset = queryset.order_by(orden)
        
        # 5. Calcular estadísticas
        total_solicitudes = queryset.count()
        total_monto = queryset.aggregate(total=Sum('montoSolicitado'))['total'] or 0
        
        estadisticas = {
            'total_solicitudes': total_solicitudes,
            'total_monto': total_monto,
            'por_estado': {
                'pendientes': queryset.filter(
                    validacionResponsable=False,
                    validacionCoordinador=False
                ).count(),
                'validadas_parcialmente': queryset.filter(
                    validacionResponsable=True,
                    validacionCoordinador=False
                ).count(),
                'validadas_completamente': queryset.filter(
                    validacionResponsable=True,
                    validacionCoordinador=True
                ).count(),
                'rechazadas': queryset.filter(
                    validacionResponsable=False,
                    validacionCoordinador=True
                ).count()
            }
        }
        
        # 6. Serializar datos
        serializer = SolicitudReembolsoSerializer(queryset, many=True)
        
        # 7. Devolver respuesta en formato uniforme
        return Response({
            'success': True,
            'actividad': {
                'id': actividad.id,
                'nombre': actividad.nombreCorto,
                'descripcion': actividad.descripcion
            },
            'tarea': {
                'id': tarea.id,
                'titulo': tarea.titulo,
                'descripcion': tarea.descripcion
            },
            'estadisticas': estadisticas,
            'total_solicitudes': total_solicitudes,
            'filtros_aplicados': {
                'actividad_id': id_actividad,
                'tarea_id': id_tarea,
                'estado': estado,
                'fecha_desde': request.query_params.get('fecha_desde'),
                'fecha_hasta': request.query_params.get('fecha_hasta'),
                'ordenar_por': orden
            },
            'solicitudes': serializer.data
        })