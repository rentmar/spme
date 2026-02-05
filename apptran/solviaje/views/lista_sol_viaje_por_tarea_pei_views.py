from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Sum, Count
from django.shortcuts import get_object_or_404
from spme_actividades.models import ActividadPei, TareaActividadPei
from spme_monitoreo.models import SolicitudViajeActPei
from ..serializer.lista_sol_viaje_por_tarea_pei_serializer import SolicitudViajeActPeiSerializer

class SolicitudesViajePeiPorActividadYTareaView(APIView):
    """
    Endpoint para obtener solicitudes de viaje PEI por actividad y tarea
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
            queryset = SolicitudViajeActPei.objects.filter(
                actividad_id=id_actividad,
                tarea_id=id_tarea  # Aquí se usa tarea_id, no tarea
            ).select_related(
                'actividad', 'tarea', 'usuario',  # Incluye el campo tarea
                'responsable', 'coordinador', 'formaPago'
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
            
            # Filtro por fechas de solicitud
            fecha_desde = request.query_params.get('fecha_desde')
            fecha_hasta = request.query_params.get('fecha_hasta')
            
            if fecha_desde:
                queryset = queryset.filter(fechaSolicitud__gte=fecha_desde)
            if fecha_hasta:
                queryset = queryset.filter(fechaSolicitud__lte=fecha_hasta)
            
            # Filtro por fecha del evento
            fecha_evento = request.query_params.get('fecha_evento')
            if fecha_evento:
                queryset = queryset.filter(fechaEvento=fecha_evento)
            
            # Filtro por lugar del evento
            lugar_evento = request.query_params.get('lugar_evento')
            if lugar_evento:
                queryset = queryset.filter(lugarEvento__icontains=lugar_evento)
            
            # Filtro por usuario solicitante
            usuario_id = request.query_params.get('usuario_id')
            if usuario_id:
                queryset = queryset.filter(usuario_id=usuario_id)
            
            # Filtro por responsable
            responsable_id = request.query_params.get('responsable_id')
            if responsable_id:
                queryset = queryset.filter(responsable_id=responsable_id)
            
            # Filtro por coordinador
            coordinador_id = request.query_params.get('coordinador_id')
            if coordinador_id:
                queryset = queryset.filter(coordinador_id=coordinador_id)
            
            # Ordenar
            orden = request.query_params.get('ordenar_por', '-fechaSolicitud')
            if orden in ['fechaSolicitud', '-fechaSolicitud', 'fechaEvento', '-fechaEvento', 
                        'montoSolicitado', '-montoSolicitado', 'numeroFormulario', '-numeroFormulario',
                        'lugarEvento', '-lugarEvento']:
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
                },
                'por_lugar_evento': list(
                    queryset.values('lugarEvento')
                    .annotate(total=Count('id'))
                    .order_by('-total')
                    .values('lugarEvento', 'total')[:10]
                ) if queryset.exists() else []
            }
            
            # 6. Serializar datos
            serializer = SolicitudViajeActPeiSerializer(queryset, many=True)
            
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
                    'fecha_evento': fecha_evento,
                    'lugar_evento': lugar_evento,
                    'usuario_id': usuario_id,
                    'responsable_id': responsable_id,
                    'coordinador_id': coordinador_id,
                    'ordenar_por': orden
                },
                'solicitudes': serializer.data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)