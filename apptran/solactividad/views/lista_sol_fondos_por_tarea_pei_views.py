from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404
from spme_actividades.models import ActividadPei, TareaActividadPei
from spme_monitoreo.models import SolicitudFondosActPei
from ..serializer.lista_sol_fondos_por_tarea_pei_serializer import SolicitudFondosActPeiSerializer


class SolicitudesFondosPeiPorActividadYTareaView(APIView):
    """
    Endpoint para obtener solicitudes de fondos PEI por actividad y tarea
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
            queryset = SolicitudFondosActPei.objects.filter(
                actividad_id=id_actividad,
                tarea_id=id_tarea
            ).select_related(
                'actividad', 'tarea', 'usuario', 
                'contador', 'coordinador', 'formaPago'
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
            elif estado == 'rechazado':
                queryset = queryset.filter(
                    validacionResponsable=False,
                    validacionCoordinador=True
                )
            
            # Filtro por fechas
            fecha_desde = request.query_params.get('fecha_desde')
            fecha_hasta = request.query_params.get('fecha_hasta')
            
            if fecha_desde:
                queryset = queryset.filter(fechaSolicitud__gte=fecha_desde)
            if fecha_hasta:
                queryset = queryset.filter(fechaSolicitud__lte=fecha_hasta)
            
            # Filtro por fecha de realización
            fecha_realizacion = request.query_params.get('fecha_realizacion')
            if fecha_realizacion:
                queryset = queryset.filter(fechaRealizacionActividad=fecha_realizacion)
            
            # Filtro por usuario solicitante
            usuario_id = request.query_params.get('usuario_id')
            if usuario_id:
                queryset = queryset.filter(usuario_id=usuario_id)
            
            # Ordenar
            orden = request.query_params.get('ordenar_por', '-fechaSolicitud')
            if orden in ['fechaSolicitud', '-fechaSolicitud', 'montoSolicitado', 
                        '-montoSolicitado', 'numeroFormulario', '-numeroFormulario',
                        'fechaRealizacionActividad', '-fechaRealizacionActividad']:
                queryset = queryset.order_by(orden)
            
            # 5. Calcular estadísticas
            total_solicitudes = queryset.count()
            total_monto = queryset.aggregate(total=Sum('montoSolicitado'))['total'] or 0
            
            estadisticas = {
                'total_solicitudes': total_solicitudes,
                'total_monto': float(total_monto),
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
            serializer = SolicitudFondosActPeiSerializer(queryset, many=True)
            
            # 7. Devolver respuesta
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
                    'fecha_desde': fecha_desde,
                    'fecha_hasta': fecha_hasta,
                    'fecha_realizacion': fecha_realizacion,
                    'usuario_id': usuario_id,
                    'ordenar_por': orden
                },
                'solicitudes': serializer.data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)