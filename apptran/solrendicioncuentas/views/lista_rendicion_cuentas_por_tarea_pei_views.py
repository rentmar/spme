from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Sum, Count
from django.db.models.functions import ExtractMonth, ExtractYear
from django.shortcuts import get_object_or_404
from spme_actividades.models import ActividadPei, TareaActividadPei
from spme_monitoreo.models import RendicionCuentasActPei
from ..serializer.lista_rendicion_cuentas_por_tarea_pei_serializer import RendicionCuentasActPeiSerializer


class RendicionesCuentasPeiPorActividadYTareaView(APIView):
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
            queryset = RendicionCuentasActPei.objects.filter(
                actividad_id=id_actividad,
                tarea_id=id_tarea
            ).select_related(
                'usuario', 'responsable', 'coordinador', 
                'contador', 'administrador', 'actividad', 'tarea',
                'solicitudFondos', 'solicitudReembolso', 
                'solicitudViaje', 'solicitudPagoDirecto'
            )
            
            # Filtro por estado
            estado = request.query_params.get('estado')
            if estado == 'pendiente':
                queryset = queryset.filter(
                    validacionResponsable=False,
                    validacionCoordinador=False,
                    validacionContador=False,
                    validacionAdministrador=False
                )
            elif estado == 'parcial':
                queryset = queryset.filter(
                    Q(validacionResponsable=True) | 
                    Q(validacionCoordinador=True) | 
                    Q(validacionContador=True) | 
                    Q(validacionAdministrador=True)
                ).exclude(
                    validacionResponsable=True,
                    validacionCoordinador=True,
                    validacionContador=True,
                    validacionAdministrador=True
                )
            elif estado == 'completo':
                queryset = queryset.filter(
                    validacionResponsable=True,
                    validacionCoordinador=True,
                    validacionContador=True,
                    validacionAdministrador=True
                )
            
            # Filtros por fecha
            fecha_desde = request.query_params.get('fecha_desde')
            fecha_hasta = request.query_params.get('fecha_hasta')
            fecha_actividad_desde = request.query_params.get('fecha_actividad_desde')
            fecha_actividad_hasta = request.query_params.get('fecha_actividad_hasta')
            fecha_rendicion_desde = request.query_params.get('fecha_rendicion_desde')
            fecha_rendicion_hasta = request.query_params.get('fecha_rendicion_hasta')
            
            if fecha_desde:
                queryset = queryset.filter(fechaDesembolso__gte=fecha_desde)
            if fecha_hasta:
                queryset = queryset.filter(fechaDesembolso__lte=fecha_hasta)
            if fecha_actividad_desde:
                queryset = queryset.filter(fechaActividad__gte=fecha_actividad_desde)
            if fecha_actividad_hasta:
                queryset = queryset.filter(fechaActividad__lte=fecha_actividad_hasta)
            if fecha_rendicion_desde:
                queryset = queryset.filter(fechaRendicion__gte=fecha_rendicion_desde)
            if fecha_rendicion_hasta:
                queryset = queryset.filter(fechaRendicion__lte=fecha_rendicion_hasta)
            
            # Filtro por montos
            monto_asignado_min = request.query_params.get('monto_asignado_min')
            monto_asignado_max = request.query_params.get('monto_asignado_max')
            monto_descargado_min = request.query_params.get('monto_descargado_min')
            monto_descargado_max = request.query_params.get('monto_descargado_max')
            
            if monto_asignado_min:
                try:
                    queryset = queryset.filter(montoAsignado__gte=float(monto_asignado_min))
                except (ValueError, TypeError):
                    pass
            if monto_asignado_max:
                try:
                    queryset = queryset.filter(montoAsignado__lte=float(monto_asignado_max))
                except (ValueError, TypeError):
                    pass
            if monto_descargado_min:
                try:
                    queryset = queryset.filter(montoDescargado__gte=float(monto_descargado_min))
                except (ValueError, TypeError):
                    pass
            if monto_descargado_max:
                try:
                    queryset = queryset.filter(montoDescargado__lte=float(monto_descargado_max))
                except (ValueError, TypeError):
                    pass
            
            # Filtro por usuarios
            usuario_id = request.query_params.get('usuario_id')
            responsable_id = request.query_params.get('responsable_id')
            coordinador_id = request.query_params.get('coordinador_id')
            contador_id = request.query_params.get('contador_id')
            administrador_id = request.query_params.get('administrador_id')
            
            if usuario_id:
                queryset = queryset.filter(usuario_id=usuario_id)
            if responsable_id:
                queryset = queryset.filter(responsable_id=responsable_id)
            if coordinador_id:
                queryset = queryset.filter(coordinador_id=coordinador_id)
            if contador_id:
                queryset = queryset.filter(contador_id=contador_id)
            if administrador_id:
                queryset = queryset.filter(administrador_id=administrador_id)
            
            # Filtro por tipo de solicitud
            tipo_solicitud = request.query_params.get('tipo_solicitud')
            if tipo_solicitud == 'fondos':
                queryset = queryset.filter(solicitudFondos__isnull=False)
            elif tipo_solicitud == 'reembolso':
                queryset = queryset.filter(solicitudReembolso__isnull=False)
            elif tipo_solicitud == 'viaje':
                queryset = queryset.filter(solicitudViaje__isnull=False)
            elif tipo_solicitud == 'pago_directo':
                queryset = queryset.filter(solicitudPagoDirecto__isnull=False)
            
            # Búsqueda por texto
            busqueda = request.query_params.get('busqueda')
            if busqueda:
                queryset = queryset.filter(
                    Q(numeroFormulario__icontains=busqueda) |
                    Q(cpteDiario__icontains=busqueda) |
                    Q(descripcionActividad__icontains=busqueda) |
                    Q(lugarActividad__icontains=busqueda) |
                    Q(lugarRendicion__icontains=busqueda)
                )
            
            # Ordenar
            orden = request.query_params.get('orden', '-fechaRendicion')
            queryset = queryset.order_by(orden)
            
            # Calcular estadísticas
            total_solicitudes = queryset.count()
            total_monto_asignado = queryset.aggregate(total=Sum('montoAsignado'))['total'] or 0
            total_monto_descargado = queryset.aggregate(total=Sum('montoDescargado'))['total'] or 0
            total_saldo = queryset.aggregate(total=Sum('saldo'))['total'] or 0
            
            # Estadísticas por tipo de solicitud
            stats_tipo_solicitud = {
                'fondos': queryset.filter(solicitudFondos__isnull=False).count(),
                'reembolso': queryset.filter(solicitudReembolso__isnull=False).count(),
                'viaje': queryset.filter(solicitudViaje__isnull=False).count(),
                'pago_directo': queryset.filter(solicitudPagoDirecto__isnull=False).count()
            }
            
            # Estadísticas por mes
            stats_mes = list(
                queryset.annotate(
                    year=ExtractYear('fechaRendicion'),
                    month=ExtractMonth('fechaRendicion')
                )
                .values('year', 'month')
                .annotate(
                    total=Count('id'),
                    monto_asignado_total=Sum('montoAsignado'),
                    monto_descargado_total=Sum('montoDescargado'),
                    saldo_total=Sum('saldo')
                )
                .order_by('year', 'month')
            )
            
            # Calcular estados
            estados = {
                'pendientes': queryset.filter(
                    validacionResponsable=False,
                    validacionCoordinador=False,
                    validacionContador=False,
                    validacionAdministrador=False
                ).count(),
                'parciales': queryset.filter(
                    Q(validacionResponsable=True) | 
                    Q(validacionCoordinador=True) | 
                    Q(validacionContador=True) | 
                    Q(validacionAdministrador=True)
                ).exclude(
                    validacionResponsable=True,
                    validacionCoordinador=True,
                    validacionContador=True,
                    validacionAdministrador=True
                ).count(),
                'completas': queryset.filter(
                    validacionResponsable=True,
                    validacionCoordinador=True,
                    validacionContador=True,
                    validacionAdministrador=True
                ).count()
            }
            
            estadisticas = {
                'total_solicitudes': total_solicitudes,
                'total_monto_asignado': float(total_monto_asignado),
                'total_monto_descargado': float(total_monto_descargado),
                'total_saldo': float(total_saldo),
                'promedio_asignado': float(total_monto_asignado / total_solicitudes) if total_solicitudes > 0 else 0,
                'promedio_descargado': float(total_monto_descargado / total_solicitudes) if total_solicitudes > 0 else 0,
                'por_estado': estados,
                'por_tipo_solicitud': stats_tipo_solicitud,
                'por_mes': stats_mes
            }
            
            # Serializar
            serializer = RendicionCuentasActPeiSerializer(queryset, many=True)
            
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
                    'fechas_desembolso': {
                        'desde': fecha_desde,
                        'hasta': fecha_hasta
                    },
                    'fechas_actividad': {
                        'desde': fecha_actividad_desde,
                        'hasta': fecha_actividad_hasta
                    },
                    'fechas_rendicion': {
                        'desde': fecha_rendicion_desde,
                        'hasta': fecha_rendicion_hasta
                    },
                    'montos_asignados': {
                        'min': monto_asignado_min,
                        'max': monto_asignado_max
                    },
                    'montos_descargados': {
                        'min': monto_descargado_min,
                        'max': monto_descargado_max
                    },
                    'usuarios': {
                        'solicitante_id': usuario_id,
                        'responsable_id': responsable_id,
                        'coordinador_id': coordinador_id,
                        'contador_id': contador_id,
                        'administrador_id': administrador_id
                    },
                    'tipo_solicitud': tipo_solicitud,
                    'orden': orden
                },
                'solicitudes': serializer.data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)