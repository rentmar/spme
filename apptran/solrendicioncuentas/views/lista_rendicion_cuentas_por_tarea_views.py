from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Sum, Count
from django.shortcuts import get_object_or_404
from spme_monitoreo.models import RendicionCuentas
from spme_actividades.models import Actividad, TareaActividad
from ..serializer.lista_rendicion_cuentas_por_tarea_serializer import RendicionCuentasSerializer


class RendicionesPorActividadYTareaView(APIView):
    """
    Endpoint para obtener rendiciones de cuentas por actividad y tarea
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
        queryset = RendicionCuentas.objects.filter(
            actividad_id=id_actividad,
            tarea_id=id_tarea
        )
        
        # 4. Aplicar filtros
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
        
        # Ordenar
        orden = request.query_params.get('ordenar_por', '-fechaRendicion')
        queryset = queryset.order_by(orden)
        
        # 5. Calcular estadísticas
        total_rendiciones = queryset.count()
        
        estadisticas = {
            'total_rendiciones': total_rendiciones,
            'total_monto_asignado': queryset.aggregate(total=Sum('montoAsignado'))['total'] or 0,
            'total_monto_descargado': queryset.aggregate(total=Sum('montoDescargado'))['total'] or 0,
            'total_saldo': queryset.aggregate(total=Sum('saldo'))['total'] or 0,
            'por_estado': {
                'pendientes': queryset.filter(
                    validacionResponsable=False,
                    validacionCoordinador=False,
                    validacionContador=False,
                    validacionAdministrador=False
                ).count(),
                'validadas_parcialmente': queryset.filter(
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
                'validadas_completamente': queryset.filter(
                    validacionResponsable=True,
                    validacionCoordinador=True,
                    validacionContador=True,
                    validacionAdministrador=True
                ).count()
            }
        }
        
        # 6. Serializar datos
        serializer = RendicionCuentasSerializer(queryset, many=True)
        
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
            'total_rendiciones': total_rendiciones,
            'filtros_aplicados': {
                'actividad_id': id_actividad,
                'tarea_id': id_tarea,
                'estado': estado,
                'fecha_desde': request.query_params.get('fecha_desde'),
                'fecha_hasta': request.query_params.get('fecha_hasta'),
                'ordenar_por': orden
            },
            'rendiciones': serializer.data
        })