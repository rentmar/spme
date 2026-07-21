# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Prefetch
from django.shortcuts import get_object_or_404
from spme_monitoreo.models import SolicitudViaje
from spme_actividades.models import Actividad, TareaActividad
from spme_validaciones.models import ValidacionSolicitudViaje
from ..serializer.lista_sol_viaje_por_tarea_serializer import SolicitudViajeSerializer
from ..services.estado_solicitud_service import EstadoSolicitudService


class SolicitudesViajePorActividadYTareaView(APIView):
    """Endpoint para obtener solicitudes de viaje por actividad y tarea."""
    
    ESTADOS_VALIDOS = ['pendiente', 'aprobado', 'rechazada', 'sin_revisores']
    
    def get(self, request, id_actividad, id_tarea):
        actividad = get_object_or_404(Actividad, id=id_actividad)
        tarea = get_object_or_404(TareaActividad, id=id_tarea)
        
        if tarea.actividad_id != id_actividad:
            return Response({
                'success': False,
                'error': 'La tarea no pertenece a esta actividad'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = SolicitudViaje.objects.filter(
            actividad_id=id_actividad,
            tarea_id=id_tarea
        ).select_related(
            'usuario', 'formaPago', 'actividad', 'tarea'
        ).prefetch_related(
            Prefetch('validaciones', queryset=ValidacionSolicitudViaje.objects.select_related('usuarioValidador'))
        )
        
        estado = request.query_params.get('estado')
        if estado and estado in self.ESTADOS_VALIDOS:
            queryset = EstadoSolicitudService.filtrar_por_estado(queryset, estado)
        
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        if fecha_desde:
            queryset = queryset.filter(fechaSolicitud__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fechaSolicitud__lte=fecha_hasta)
        
        orden = request.query_params.get('ordenar_por', '-fechaSolicitud')
        queryset = queryset.order_by(orden)
        
        base_stats = SolicitudViaje.objects.filter(actividad_id=id_actividad, tarea_id=id_tarea)
        estadisticas = EstadoSolicitudService.get_estadisticas(base_stats)
        estadisticas['total_monto'] = queryset.aggregate(total=Sum('montoSolicitado'))['total'] or 0
        
        serializer = SolicitudViajeSerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'actividad': {'id': actividad.id, 'nombre': actividad.nombreCorto},
            'tarea': {'id': tarea.id, 'titulo': tarea.titulo},
            'estadisticas': estadisticas,
            'total_solicitudes': queryset.count(),
            'filtros_aplicados': {
                'actividad_id': id_actividad, 'tarea_id': id_tarea, 'estado': estado,
            },
            'solicitudes': serializer.data,
        })