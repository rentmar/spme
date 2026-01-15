# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Avg, Max, Min
from spme_planificacion.models import PlanificacionPei
from ..serializers.planificacion_pei_seguimiento_historial_serializer import SeguimientoPeiSerializer

class SeguimientoPeiView(APIView):
    """
    Endpoint para obtener seguimiento de un PEI
    Ordenado por fecha de creación descendente (más reciente primero)
    """
    
    def get(self, request, pei_id):
        """
        GET /api/seguimiento-pei/{pei_id}/
        
        Obtiene todas las versiones de planificación de un PEI,
        ordenadas por fecha de CREACIÓN (la más reciente primero)
        
        Parámetros opcionales:
        - orden: 'asc' (ascendente) o 'desc' (descendente, default)
        - limite: número máximo de registros a retornar
        """
        try:
            # Obtener parámetros de consulta
            orden = request.GET.get('orden', 'desc').lower()
            limite = request.GET.get('limite')
            
            # Base queryset filtrado por PEI
            queryset = PlanificacionPei.objects.filter(pei_id=pei_id)
            
            # Verificar si hay registros
            if not queryset.exists():
                return Response(
                    {
                        'success': True,
                        'pei_id': pei_id,
                        'mensaje': 'No se encontraron registros para este PEI',
                        'total_registros': 0,
                        'registros': []
                    },
                    status=status.HTTP_200_OK
                )
            
            # Aplicar ORDENAMIENTO por creado_el
            if orden == 'asc':
                # Ascendente: más antiguo primero
                queryset = queryset.order_by('creado_el')
                ordenamiento = 'fecha_creacion_ascendente'
            else:
                # Descendente: más reciente primero (default)
                queryset = queryset.order_by('-creado_el')
                ordenamiento = 'fecha_creacion_descendente'
            
            # Aplicar límite si se especifica
            if limite and limite.isdigit():
                limite_int = int(limite)
                queryset = queryset[:limite_int]
                aplico_limite = True
            else:
                aplico_limite = False
            
            # Optimizar consultas con select_related
            queryset = queryset.select_related(
                'creado_por',
                'actualizado_por',
                'pei'
            )
            
            # Serializar datos
            serializer = SeguimientoPeiSerializer(queryset, many=True)
            
            # Obtener estadísticas sobre fechas de creación
            estadisticas_fechas = self._obtener_estadisticas_fechas(pei_id)
            
            # Preparar respuesta detallada
            response_data = {
                'success': True,
                'pei_id': pei_id,
                'parametros_aplicados': {
                    'orden': orden,
                    'ordenamiento_aplicado': ordenamiento,
                    'limite': limite if aplico_limite else 'sin_limite',
                    'registros_solicitados': limite if aplico_limite else 'todos'
                },
                'estadisticas': {
                    'total_registros': PlanificacionPei.objects.filter(pei_id=pei_id).count(),
                    'registros_devueltos': len(serializer.data),
                    'fechas_creacion': estadisticas_fechas,
                    'rango_versiones': {
                        'minima': queryset.aggregate(Min('version'))['version__min'],
                        'maxima': queryset.aggregate(Max('version'))['version__max'],
                    }
                },
                'registros': serializer.data
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response(
                {
                    'success': False,
                    'error': 'Parámetro inválido',
                    'detalle': str(e),
                    'pei_id': pei_id
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'error': 'Error interno del servidor',
                    'detalle': str(e),
                    'pei_id': pei_id
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _obtener_estadisticas_fechas(self, pei_id):
        """Obtener estadísticas sobre las fechas de creación"""
        try:
            registros = PlanificacionPei.objects.filter(pei_id=pei_id)
            
            if not registros.exists():
                return {}
            
            # Obtener todas las fechas de creación
            fechas = registros.values_list('creado_el', flat=True)
            fechas_lista = list(fechas)
            
            # Calcular estadísticas
            primera = min(fechas_lista)
            ultima = max(fechas_lista)
            
            # Calcular diferencia en días
            from datetime import datetime
            if isinstance(primera, datetime) and isinstance(ultima, datetime):
                diferencia_dias = (ultima - primera).days
            else:
                diferencia_dias = None
            
            return {
                'primera_creacion': primera.isoformat() if primera else None,
                'ultima_creacion': ultima.isoformat() if ultima else None,
                'periodo_total_dias': diferencia_dias,
                'total_fechas_unicas': len(set(fechas_lista))
            }
            
        except Exception:
            return {}