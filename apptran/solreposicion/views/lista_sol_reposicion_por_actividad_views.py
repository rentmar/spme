# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Prefetch
from spme_monitoreo.models import SolicitudReembolso
from spme_actividades.models import Actividad
from spme_validaciones.models import ValidacionSolicitudReembolso
from ..serializers.lista_sol_reposicion_por_actividad_serializer import SolicitudReembolsoSimpleSerializer
from ..services.estado_solicitud_service import EstadoSolicitudService


class SolicitudesReembolsoSinTareaPorActividadView(APIView):
    """Endpoint para obtener solicitudes de REEMBOLSO por idActividad (sin tarea)."""
    
    ESTADOS_VALIDOS = ['pendiente', 'aprobado', 'rechazada', 'sin_revisores']
    
    def get(self, request, id_actividad):
        try:
            actividad = Actividad.objects.get(id=id_actividad)
        except Actividad.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Actividad con ID {id_actividad} no encontrada',
            }, status=status.HTTP_404_NOT_FOUND)
        
        queryset = SolicitudReembolso.objects.filter(
            actividad_id=id_actividad,
            tarea__isnull=True
        ).select_related(
            'usuario', 'formaPago', 'actividad'
        ).prefetch_related(
            Prefetch('validaciones', queryset=ValidacionSolicitudReembolso.objects.select_related('usuarioValidador'))
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
        
        ordenar_por = request.query_params.get('ordenar_por', '-fechaSolicitud')
        campos_permitidos = [
            'fechaSolicitud', '-fechaSolicitud',
            'montoSolicitado', '-montoSolicitado',
            'numeroFormulario', '-numeroFormulario',
        ]
        queryset = queryset.order_by(ordenar_por if ordenar_por in campos_permitidos else '-fechaSolicitud')
        
        base_stats = SolicitudReembolso.objects.filter(actividad_id=id_actividad, tarea__isnull=True)
        estadisticas = EstadoSolicitudService.get_estadisticas(base_stats)
        estadisticas['total_monto'] = queryset.aggregate(total=Sum('montoSolicitado'))['total'] or 0
        
        total_solicitudes = queryset.count()
        
        pagina = request.query_params.get('pagina')
        por_pagina = request.query_params.get('por_pagina', 20)
        
        if pagina and por_pagina.isdigit():
            try:
                pagina = int(pagina)
                por_pagina = int(por_pagina)
                inicio = (pagina - 1) * por_pagina
                solicitudes_paginadas = list(queryset[inicio:inicio + por_pagina])
                total_paginas = (total_solicitudes + por_pagina - 1) // por_pagina
                
                serializer = SolicitudReembolsoSimpleSerializer(solicitudes_paginadas, many=True)
                
                return Response({
                    'success': True,
                    'actividad': {'id': actividad.id, 'nombre': actividad.nombreCorto},
                    'estadisticas': estadisticas,
                    'paginacion': {
                        'pagina_actual': pagina, 'por_pagina': por_pagina,
                        'total_solicitudes': total_solicitudes, 'total_paginas': total_paginas,
                    },
                    'filtros_aplicados': {'tarea_nula': True, 'estado': estado},
                    'solicitudes': serializer.data,
                })
            except (ValueError, IndexError):
                pass
        
        serializer = SolicitudReembolsoSimpleSerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'actividad': {'id': actividad.id, 'nombre': actividad.nombreCorto},
            'estadisticas': estadisticas,
            'total_solicitudes': total_solicitudes,
            'filtros_aplicados': {'tarea_nula': True, 'estado': estado},
            'solicitudes': serializer.data,
        })