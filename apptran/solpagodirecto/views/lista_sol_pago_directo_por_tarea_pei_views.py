from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Sum, Count
from django.shortcuts import get_object_or_404
from spme_actividades.models import ActividadPei, TareaActividadPei
from spme_monitoreo.models import SolicitudPagoDirectoActPei
from ..serializer.lista_sol_pago_directo_por_tarea_pei_serializer import SolicitudPagoDirectoActPeiSerializer

class SolicitudesPagoDirectoPeiPorActividadYTareaView(APIView):
    """
    Endpoint para obtener solicitudes de pago directo PEI por actividad y tarea
    """
    
    def get(self, request, id_actividad, id_tarea):
        try:
            # 1. Validar que existen
            actividad = get_object_or_404(ActividadPei, id=id_actividad)
            tarea = get_object_or_404(TareaActividadPei, id=id_tarea)
            
            # 2. Validar relación
            if tarea.actividad_id != id_actividad:
                return Response({
                    'success': False,
                    'error': 'La tarea no pertenece a esta actividad'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 3. Obtener queryset base
            queryset = SolicitudPagoDirectoActPei.objects.filter(
                actividad_id=id_actividad,
                tarea_id=id_tarea
            ).select_related(
                'actividad', 'tarea', 'usuario', 
                'contador', 'coordinador', 'formaPago'
            )
            
            # 4. Aplicar filtros básicos
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
            
            # 5. Filtros por fecha
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
            
            # 6. Filtro por monto
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
            
            # 7. Filtro por forma de pago
            forma_pago_id = request.query_params.get('forma_pago_id')
            if forma_pago_id:
                queryset = queryset.filter(formaPago_id=forma_pago_id)
            
            # 8. Filtro por usuarios
            usuario_id = request.query_params.get('usuario_id')
            contador_id = request.query_params.get('contador_id')
            coordinador_id = request.query_params.get('coordinador_id')
            
            if usuario_id:
                queryset = queryset.filter(usuario_id=usuario_id)
            if contador_id:
                queryset = queryset.filter(contador_id=contador_id)
            if coordinador_id:
                queryset = queryset.filter(coordinador_id=coordinador_id)
            
            # 9. Búsqueda por texto
            busqueda = request.query_params.get('busqueda')
            if busqueda:
                queryset = queryset.filter(
                    Q(descripcion_actividad__icontains=busqueda) |
                    Q(objetivo_actividad__icontains=busqueda) |
                    Q(lugarSolicitud__icontains=busqueda) |
                    Q(numeroFormulario__icontains=busqueda)
                )
            
            # 10. Ordenar
            orden = request.query_params.get('ordenar_por', '-fechaSolicitud')
            ordenes_validos = {
                'fecha_solicitud': 'fechaSolicitud',
                '-fecha_solicitud': '-fechaSolicitud',
                'fecha_realizacion': 'fechaRealizacionActividad',
                '-fecha_realizacion': '-fechaRealizacionActividad',
                'monto': 'montoSolicitado',
                '-monto': '-montoSolicitado',
                'numero': 'numeroFormulario',
                '-numero': '-numeroFormulario'
            }
            
            if orden in ordenes_validos:
                queryset = queryset.order_by(ordenes_validos[orden])
            
            # 11. Calcular estadísticas
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
                .values('formaPago__formaPago', 'total', 'monto_total')[:10]
            ) if queryset.exists() else []
            
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
                'por_mes': self._get_estadisticas_por_mes(queryset) if total_solicitudes > 0 else []
            }
            
            # 12. Serializar datos
            serializer = SolicitudPagoDirectoActPeiSerializer(queryset, many=True)
            
            # 13. Devolver respuesta
            return Response({
                'success': True,
                'actividad': {
                    'id': actividad.id,
                    'nombre_corto': actividad.nombreCorto if hasattr(actividad, 'nombreCorto') else 'Sin nombre',
                    'codigo': actividad.codigo if hasattr(actividad, 'codigo') else None,
                    'descripcion': actividad.descripcion if hasattr(actividad, 'descripcion') else None
                },
                'tarea': {
                    'id': tarea.id,
                    'titulo': tarea.titulo if hasattr(tarea, 'titulo') else 'Sin título',
                    'descripcion': tarea.descripcion if hasattr(tarea, 'descripcion') else None,
                    'estado': tarea.estado if hasattr(tarea, 'estado') else None
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
                    'monto': {'min': monto_min, 'max': monto_max},
                    'forma_pago_id': forma_pago_id,
                    'usuarios': {
                        'solicitante_id': usuario_id,
                        'contador_id': contador_id,
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
    
    def _get_estadisticas_por_mes(self, queryset):
        """
        Método auxiliar para obtener estadísticas por mes
        """
        from django.db.models.functions import ExtractMonth, ExtractYear
        
        return list(
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