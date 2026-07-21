# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Prefetch
from spme_monitoreo.models import SolicitudFondos
from spme_actividades.models import Actividad
from spme_validaciones.models import ValidacionSolicitudFondos
from ..serializer.lista_sol_fondos_por_actividad_serializer import SolicitudFondosSimpleSerializer
from ..services.estado_solicitud_service import EstadoSolicitudService


class SolicitudesPorActividadConTareaNulaView(APIView):
    """
    Endpoint para obtener solicitudes de fondos por idActividad.
    FILTRADO: Solo solicitudes SIN tarea (tarea__isnull=True).
    
    GET /api/actividades/{id_actividad}/solicitudes-sin-tarea/
    
    Parámetros opcionales:
    - estado: pendiente | aprobada | rechazada | sin_revisores
    - fecha_desde: YYYY-MM-DD
    - fecha_hasta: YYYY-MM-DD
    - ordenar_por: fechaSolicitud | -fechaSolicitud | montoSolicitado | -montoSolicitado
    - pagina: número de página
    - por_pagina: items por página (default 20)
    """
    
    ESTADOS_VALIDOS = ['pendiente', 'aprobado', 'rechazada', 'sin_revisores']
    
    def get(self, request, id_actividad):
        # 1. Verificar actividad
        try:
            actividad = Actividad.objects.get(id=id_actividad)
        except Actividad.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Actividad con ID {id_actividad} no encontrada',
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 2. Queryset base
        queryset = SolicitudFondos.objects.filter(
            actividad_id=id_actividad,
            tarea__isnull=True
        ).select_related(
            'usuario', 'formaPago', 'actividad'
        ).prefetch_related(
            Prefetch(
                'validaciones',
                queryset=ValidacionSolicitudFondos.objects.select_related('usuarioValidador')
            )
        )
        
        # 3. Filtro por estado
        estado = request.query_params.get('estado')
        if estado and estado in self.ESTADOS_VALIDOS:
            queryset = EstadoSolicitudService.filtrar_por_estado(queryset, estado)
        
        # 4. Filtros de fecha
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        if fecha_desde:
            queryset = queryset.filter(fechaSolicitud__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fechaSolicitud__lte=fecha_hasta)
        
        # 5. Ordenamiento
        ordenar_por = request.query_params.get('ordenar_por', '-fechaSolicitud')
        campos_permitidos = [
            'fechaSolicitud', '-fechaSolicitud',
            'montoSolicitado', '-montoSolicitado',
            'numeroFormulario', '-numeroFormulario',
        ]
        queryset = queryset.order_by(
            ordenar_por if ordenar_por in campos_permitidos else '-fechaSolicitud'
        )
        
        # 6. Estadísticas (sobre el total sin paginar)
        base_stats = SolicitudFondos.objects.filter(
            actividad_id=id_actividad,
            tarea__isnull=True
        )
        estadisticas = EstadoSolicitudService.get_estadisticas(base_stats)
        estadisticas['total_monto'] = queryset.aggregate(
            total=Sum('montoSolicitado')
        )['total'] or 0
        
        # 7. Paginación
        pagina = request.query_params.get('pagina')
        por_pagina = int(request.query_params.get('por_pagina', 20))
        total_solicitudes = queryset.count()
        
        if pagina and str(por_pagina).isdigit():
            try:
                pagina = int(pagina)
                inicio = (pagina - 1) * por_pagina
                solicitudes_paginadas = list(queryset[inicio:inicio + por_pagina])
                total_paginas = (total_solicitudes + por_pagina - 1) // por_pagina
                
                serializer = SolicitudFondosSimpleSerializer(solicitudes_paginadas, many=True)
                
                return Response({
                    'success': True,
                    'actividad': {
                        'id': actividad.id,
                        'nombre': getattr(actividad, 'nombre', ''),
                    },
                    'estadisticas': estadisticas,
                    'paginacion': {
                        'pagina_actual': pagina,
                        'por_pagina': por_pagina,
                        'total_solicitudes': total_solicitudes,
                        'total_paginas': total_paginas,
                    },
                    'filtros_aplicados': {
                        'tarea_nula': True,
                        'estado': estado,
                        'fecha_desde': fecha_desde,
                        'fecha_hasta': fecha_hasta,
                        'ordenar_por': ordenar_por,
                    },
                    'solicitudes': serializer.data,
                })
            except (ValueError, IndexError):
                pass
        
        # 8. Sin paginación
        serializer = SolicitudFondosSimpleSerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'actividad': {
                'id': actividad.id,
                'nombre': getattr(actividad, 'nombre', ''),
            },
            'estadisticas': estadisticas,
            'total_solicitudes': total_solicitudes,
            'filtros_aplicados': {
                'tarea_nula': True,
                'estado': estado,
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta,
                'ordenar_por': ordenar_por,
            },
            'solicitudes': serializer.data,
        })