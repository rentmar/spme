# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Prefetch
from spme_monitoreo.models import RendicionCuentas
from spme_actividades.models import Actividad
from spme_validaciones.models import ValidacionRendicionCuentas
from ..serializer.lista_rendicion_cuentas_por_actividad_serializer import RendicionCuentasSimpleSerializer
from ..services.estado_solicitud_service import EstadoSolicitudService


class RendicionesSinTareaPorActividadView(APIView):
    """Endpoint para obtener RENDICIONES DE CUENTAS por idActividad (sin tarea)."""
    
    ESTADOS_VALIDOS = ['pendiente', 'aprobado', 'rechazada', 'sin_revisores']
    
    def get(self, request, id_actividad):
        try:
            actividad = Actividad.objects.get(id=id_actividad)
        except Actividad.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Actividad con ID {id_actividad} no encontrada',
            }, status=status.HTTP_404_NOT_FOUND)
        
        queryset = RendicionCuentas.objects.filter(
            actividad_id=id_actividad,
            tarea__isnull=True
        ).select_related(
            'usuario', 'actividad'
        ).prefetch_related(
            Prefetch('validaciones', queryset=ValidacionRendicionCuentas.objects.select_related('usuarioValidador'))
        )
        
        estado = request.query_params.get('estado')
        if estado and estado in self.ESTADOS_VALIDOS:
            queryset = EstadoSolicitudService.filtrar_por_estado(queryset, estado)
        
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        if fecha_desde:
            queryset = queryset.filter(fechaRendicion__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fechaRendicion__lte=fecha_hasta)
        
        ordenar_por = request.query_params.get('ordenar_por', '-fechaRendicion')
        campos_permitidos = [
            'fechaRendicion', '-fechaRendicion',
            'montoAsignado', '-montoAsignado',
            'numeroFormulario', '-numeroFormulario',
        ]
        queryset = queryset.order_by(ordenar_por if ordenar_por in campos_permitidos else '-fechaRendicion')
        
        base_stats = RendicionCuentas.objects.filter(actividad_id=id_actividad, tarea__isnull=True)
        estadisticas = EstadoSolicitudService.get_estadisticas(base_stats)
        estadisticas['total_monto_asignado'] = queryset.aggregate(total=Sum('montoAsignado'))['total'] or 0
        estadisticas['total_monto_descargado'] = queryset.aggregate(total=Sum('montoDescargado'))['total'] or 0
        estadisticas['total_saldo'] = queryset.aggregate(total=Sum('saldo'))['total'] or 0
        
        total_rendiciones = queryset.count()
        
        pagina = request.query_params.get('pagina')
        por_pagina = request.query_params.get('por_pagina', 20)
        
        if pagina and por_pagina.isdigit():
            try:
                pagina = int(pagina)
                por_pagina = int(por_pagina)
                inicio = (pagina - 1) * por_pagina
                rendiciones_paginadas = list(queryset[inicio:inicio + por_pagina])
                total_paginas = (total_rendiciones + por_pagina - 1) // por_pagina
                
                serializer = RendicionCuentasSimpleSerializer(rendiciones_paginadas, many=True)
                
                return Response({
                    'success': True,
                    'actividad': {'id': actividad.id, 'nombre': actividad.nombreCorto},
                    'estadisticas': estadisticas,
                    'paginacion': {
                        'pagina_actual': pagina, 'por_pagina': por_pagina,
                        'total_rendiciones': total_rendiciones, 'total_paginas': total_paginas,
                    },
                    'filtros_aplicados': {'tarea_nula': True, 'estado': estado},
                    'rendiciones': serializer.data,
                })
            except (ValueError, IndexError):
                pass
        
        serializer = RendicionCuentasSimpleSerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'actividad': {'id': actividad.id, 'nombre': actividad.nombreCorto},
            'estadisticas': estadisticas,
            'total_rendiciones': total_rendiciones,
            'filtros_aplicados': {'tarea_nula': True, 'estado': estado},
            'rendiciones': serializer.data,
        })