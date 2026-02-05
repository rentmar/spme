from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Sum, Count
from django.shortcuts import get_object_or_404
from spme_actividades.models import ActividadPei, TareaActividadPei
from spme_monitoreo.models import SolicitudReembolsoActPei
from ..serializers.lista_sol_reposicion_por_tarea_pei_serializer import SolicitudReembolsoActPeiSerializer
from django.db.models.functions import ExtractMonth, ExtractYear

class SolicitudesReembolsoPeiPorActividadYTareaView(APIView):
    def get(self, request, id_actividad, id_tarea):
        try:
            # Validar que existen
            actividad = get_object_or_404(ActividadPei, id=id_actividad)
            tarea = get_object_or_404(TareaActividadPei, id=id_tarea)
            
            # Validar relación
            if tarea.actividad_id != id_actividad:
                return Response({
                    'success': False,
                    'error': 'La tarea no pertenece a esta actividad'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener queryset base
            queryset = SolicitudReembolsoActPei.objects.filter(
                actividad_id=id_actividad,
                tarea_id=id_tarea
            ).select_related('formaPago', 'usuario', 'responsable', 'coordinador')
            
            # Filtro por estado
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
            elif estado == 'rechazado':
                queryset = queryset.filter(
                    validacionResponsable=False,
                    validacionCoordinador=True
                )
            
            # Filtros por fecha
            fecha_solicitud_desde = request.query_params.get('fecha_solicitud_desde')
            fecha_solicitud_hasta = request.query_params.get('fecha_solicitud_hasta')
            fecha_realizacion_desde = request.query_params.get('fecha_realizacion_desde')
            fecha_realizacion_hasta = request.query_params.get('fecha_realizacion_hasta')
            
            if fecha_solicitud_desde:
                queryset = queryset.filter(fechaSolicitud__gte=fecha_solicitud_desde)
            if fecha_solicitud_hasta:
                queryset = queryset.filter(fechaSolicitud__lte=fecha_solicitud_hasta)
            if fecha_realizacion_desde:
                queryset = queryset.filter(fechaRealizacionActividad__gte=fecha_realizacion_desde)
            if fecha_realizacion_hasta:
                queryset = queryset.filter(fechaRealizacionActividad__lte=fecha_realizacion_hasta)
            
            # Filtro por monto
            monto_min = request.query_params.get('monto_min')
            monto_max = request.query_params.get('monto_max')
            
            if monto_min:
                try:
                    queryset = queryset.filter(montoSolicitado__gte=float(monto_min))
                except (ValueError, TypeError):
                    pass
            if monto_max:
                try:
                    queryset = queryset.filter(montoSolicitado__lte=float(monto_max))
                except (ValueError, TypeError):
                    pass
            
            # Filtro por forma de pago
            forma_pago_id = request.query_params.get('forma_pago_id')
            if forma_pago_id:
                queryset = queryset.filter(formaPago_id=forma_pago_id)
            
            # Filtro por usuarios
            usuario_id = request.query_params.get('usuario_id')
            responsable_id = request.query_params.get('responsable_id')
            coordinador_id = request.query_params.get('coordinador_id')
            
            if usuario_id:
                queryset = queryset.filter(usuario_id=usuario_id)
            if responsable_id:
                queryset = queryset.filter(responsable_id=responsable_id)
            if coordinador_id:
                queryset = queryset.filter(coordinador_id=coordinador_id)
            
            # Búsqueda por texto
            busqueda = request.query_params.get('busqueda')
            if busqueda:
                queryset = queryset.filter(
                    Q(descripcion_actividad__icontains=busqueda) |
                    Q(objetivo_actividad__icontains=busqueda) |
                    Q(lugarSolicitud__icontains=busqueda) |
                    Q(numeroFormulario__icontains=busqueda)
                )
            
            # Ordenar
            orden = request.query_params.get('orden', '-fechaSolicitud')
            queryset = queryset.order_by(orden)
            
            # Calcular estadísticas
            total_solicitudes = queryset.count()
            total_monto = queryset.aggregate(total=Sum('montoSolicitado'))['total'] or 0
            
            # Estadísticas por forma de pago
            stats_forma_pago = list(
                queryset.values('formaPago__formaPago')
                .annotate(
                    total=Count('id'),
                    monto_total=Sum('montoSolicitado')
                )
                .order_by('-monto_total')
                .values('formaPago__formaPago', 'total', 'monto_total')
            )
            
            # Estadísticas por mes
            stats_mes = list(
                queryset.annotate(
                    year=ExtractYear('fechaSolicitud'),
                    month=ExtractMonth('fechaSolicitud')
                )
                .values('year', 'month')
                .annotate(
                    total=Count('id'),
                    monto_total=Sum('montoSolicitado')
                )
                .order_by('year', 'month')
            )
            
            estadisticas = {
                'total_solicitudes': total_solicitudes,
                'total_monto': float(total_monto),
                'promedio_monto': float(total_monto / total_solicitudes) if total_solicitudes > 0 else 0,
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
                },
                'por_forma_pago': stats_forma_pago,
                'por_mes': stats_mes
            }
            
            # Serializar
            serializer = SolicitudReembolsoActPeiSerializer(queryset, many=True)
            
            return Response({
                'success': True,
                'actividad': {
                    'id': actividad.id,
                    'nombre_corto': actividad.nombreCorto if hasattr(actividad, 'nombreCorto') else '',
                    'codigo': actividad.codigo if hasattr(actividad, 'codigo') else '',
                    'descripcion': actividad.descripcion if hasattr(actividad, 'descripcion') else ''
                },
                'tarea': {
                    'id': tarea.id,
                    'titulo': tarea.titulo if hasattr(tarea, 'titulo') else '',
                    'descripcion': tarea.descripcion if hasattr(tarea, 'descripcion') else '',
                    'estado': tarea.estado if hasattr(tarea, 'estado') else ''
                },
                'estadisticas': estadisticas,
                'total_solicitudes': total_solicitudes,
                'filtros_aplicados': {
                    'actividad_id': id_actividad,
                    'tarea_id': id_tarea,
                    'estado': estado,
                    'busqueda': busqueda,
                    'fechas_solicitud': {
                        'desde': fecha_solicitud_desde,
                        'hasta': fecha_solicitud_hasta
                    },
                    'fechas_realizacion': {
                        'desde': fecha_realizacion_desde,
                        'hasta': fecha_realizacion_hasta
                    },
                    'monto': {
                        'min': monto_min,
                        'max': monto_max
                    },
                    'forma_pago_id': forma_pago_id,
                    'usuarios': {
                        'solicitante_id': usuario_id,
                        'responsable_id': responsable_id,
                        'coordinador_id': coordinador_id
                    },
                    'orden': orden
                },
                'solicitudes': serializer.data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)