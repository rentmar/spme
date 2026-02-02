from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from django.db.models import Prefetch, Count
from rest_framework.generics import ListAPIView
from django.db.models import Count, Q

from spme_actividades.models import (
    Actividad, 
    TareaActividad
    )
from spme_monitoreo.models import (
    InformeActividadPrincipal, 
    InformeTareaPrincipal
    )

from ..serializers.lista_informe_actividad_completo_serializer import (
    ActividadInformesCompletosSerializer,
    InformeTareaPrincipalSerializer,
    InformeActividadPrincipalSerializer,
    ActividadResumenSerializer,
    )

class ActividadInformesCompletosView(APIView):
    """
    Endpoint para obtener todos los informes de una actividad específica
    y los informes de sus tareas relacionadas.
    
    URL: /api/actividades/<id_actividad>/informes-completos/
    Método: GET
    """
    # permission_classes = [IsAuthenticated]
    
    def get(self, request, actividad_id=None):
        try:
            # Obtener la actividad con prefetch de relaciones
            actividad = get_object_or_404(
                Actividad.objects.select_related('tipo').prefetch_related(
                    Prefetch(
                        'actividad_informes_de_actividad_principal',
                        queryset=InformeActividadPrincipal.objects.all()
                    ),
                    Prefetch(
                        'tareas',
                        queryset=TareaActividad.objects.prefetch_related(
                            Prefetch(
                                'tarea_informes_de_subactividad_principal',
                                queryset=InformeTareaPrincipal.objects.all()
                            )
                        ).all()
                    )
                ),
                id=actividad_id,
                estaInactiva=False  # Solo actividades activas
            )
            
            # Serializar los datos
            serializer = ActividadInformesCompletosSerializer(actividad, context={'request': request})
            
            return Response({
                'success': True,
                'actividad': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Actividad.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Actividad no encontrada o está inactiva'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InformesPorFechaView(APIView):
    """
    Endpoint para filtrar informes por fecha de ejecución.
    
    URL: /api/actividades/<id_actividad>/informes-por-fecha/
    Parámetros: ?fecha_desde=YYYY-MM-DD&fecha_hasta=YYYY-MM-DD
    Método: GET
    """
    # permission_classes = [IsAuthenticated]
    
    def get(self, request, actividad_id=None):
        try:
            # Obtener parámetros de fecha
            fecha_desde = request.GET.get('fecha_desde')
            fecha_hasta = request.GET.get('fecha_hasta')
            
            # Validar que la actividad existe
            actividad = get_object_or_404(
                Actividad,
                id=actividad_id,
                estaInactiva=False
            )
            
            # Filtrar informes de la actividad principal
            informes_actividad_filtrados = actividad.actividad_informes_de_actividad_principal.all()
            
            # Filtrar informes de tareas
            informes_tareas_filtrados = []
            tareas_con_informes = []
            
            for tarea in actividad.tareas.all():
                informes_tarea = tarea.tarea_informes_de_subactividad_principal.all()
                
                # Aplicar filtros de fecha si existen
                if fecha_desde:
                    informes_tarea = informes_tarea.filter(fechaEjecucion__gte=fecha_desde)
                if fecha_hasta:
                    informes_tarea = informes_tarea.filter(fechaEjecucion__lte=fecha_hasta)
                
                if informes_tarea.exists():
                    tareas_con_informes.append({
                        'tarea': {
                            'id': tarea.id,
                            'codigo': tarea.codigo,
                            'titulo': tarea.titulo
                        },
                        'informes': informes_tarea.count(),
                        'detalle_informes': InformeTareaPrincipalSerializer(informes_tarea, many=True).data
                    })
            
            # Aplicar filtros a informes de actividad principal
            if fecha_desde:
                informes_actividad_filtrados = informes_actividad_filtrados.filter(fechaEjecucion__gte=fecha_desde)
            if fecha_hasta:
                informes_actividad_filtrados = informes_actividad_filtrados.filter(fechaEjecucion__lte=fecha_hasta)
            
            return Response({
                'success': True,
                'actividad': {
                    'id': actividad.id,
                    'codigo': actividad.codigo,
                    'nombreCorto': actividad.nombreCorto
                },
                'filtros_aplicados': {
                    'fecha_desde': fecha_desde,
                    'fecha_hasta': fecha_hasta
                },
                'informes_actividad': {
                    'total': informes_actividad_filtrados.count(),
                    'detalle': InformeActividadPrincipalSerializer(informes_actividad_filtrados, many=True).data
                },
                'tareas_con_informes': tareas_con_informes,
                'totales': {
                    'total_informes_actividad': informes_actividad_filtrados.count(),
                    'total_informes_tareas': sum(t['informes'] for t in tareas_con_informes),
                    'tareas_con_informes': len(tareas_con_informes)
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class ActividadesConResumenInformesView(ListAPIView):
    """
    Lista todas las actividades con un resumen de sus informes y tareas.
    
    Filtros disponibles:
    - estado: Filtrar por estado de actividad
    - tipo_id: Filtrar por tipo de actividad
    - proyecto_id: Filtrar por proyecto
    - responsable_id: Filtrar por responsable
    - fecha_desde: Actividades desde fecha
    - fecha_hasta: Actividades hasta fecha
    """
    # permission_classes = [IsAuthenticated]
    serializer_class = ActividadResumenSerializer
    
    def get_queryset(self):
        queryset = Actividad.objects.filter(estaInactiva=False)
        
        # Optimizar queries con select_related
        queryset = queryset.select_related(
            'tipo',
            'responsable',
            'proyecto'
        )
        
        # Anotar con conteos de informes y tareas
        queryset = queryset.annotate(
            total_informes_actividad=Count(
                'actividad_informes_de_actividad_principal',
                distinct=True
            ),
            total_tareas=Count('tareas', distinct=True),
            total_informes_tareas=Count(
                'tareas__tarea_informes_de_subactividad_principal',
                distinct=True
            )
        )
        
        # Aplicar filtros
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        tipo_id = self.request.GET.get('tipo_id')
        if tipo_id:
            queryset = queryset.filter(tipo_id=tipo_id)
        
        proyecto_id = self.request.GET.get('proyecto_id')
        if proyecto_id:
            queryset = queryset.filter(proyecto_id=proyecto_id)
        
        responsable_id = self.request.GET.get('responsable_id')
        if responsable_id:
            queryset = queryset.filter(responsable_id=responsable_id)
        
        fecha_desde = self.request.GET.get('fecha_desde')
        if fecha_desde:
            queryset = queryset.filter(fecha_programada__gte=fecha_desde)
        
        fecha_hasta = self.request.GET.get('fecha_hasta')
        if fecha_hasta:
            queryset = queryset.filter(fecha_programada__lte=fecha_hasta)
        
        # Ordenamiento
        orden = self.request.GET.get('orden', '-fecha_programada')
        if orden in ['fecha_programada', '-fecha_programada', 
                     'codigo', '-codigo', 'nombreCorto', '-nombreCorto',
                     'total_informes_general', '-total_informes_general']:
            # Para orden personalizado por total_informes_general
            if orden == 'total_informes_general':
                queryset = queryset.order_by('total_informes_actividad', 'total_informes_tareas')
            elif orden == '-total_informes_general':
                queryset = queryset.order_by('-total_informes_actividad', '-total_informes_tareas')
            else:
                queryset = queryset.order_by(orden)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        # Obtener el queryset paginado
        queryset = self.filter_queryset(self.get_queryset())
        
        # Paginación
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'success': True,
                'actividades': serializer.data,
                'estadisticas': self.get_estadisticas(queryset)
            })
        
        # Si no hay paginación
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'count': queryset.count(),
            'estadisticas': self.get_estadisticas(queryset),
            'actividades': serializer.data
        })
    
    def get_estadisticas(self, queryset):
        """Calcula estadísticas generales del queryset"""
        total_actividades = queryset.count()
        
        # Usamos annotate para calcular sumas eficientemente
        from django.db.models import Sum, Avg
        
        estadisticas = queryset.aggregate(
            total_presupuesto=Sum('presupuesto'),
            total_ejecutado=Sum('totalEjecutado'),
            avg_grado_ejecucion=Avg('gradoEjecucion'),
            total_informes_act=Sum('total_informes_actividad'),
            total_informes_tar=Sum('total_informes_tareas'),
            total_tareas=Sum('total_tareas')
        )
        
        return {
            'total_actividades': total_actividades,
            'total_presupuesto': estadisticas['total_presupuesto'] or 0,
            'total_ejecutado': estadisticas['total_ejecutado'] or 0,
            'porcentaje_ejecucion': self.calcular_porcentaje_ejecucion(
                estadisticas['total_ejecutado'] or 0,
                estadisticas['total_presupuesto'] or 0
            ),
            'promedio_grado_ejecucion': round(estadisticas['avg_grado_ejecucion'] or 0, 2),
            'total_informes': (estadisticas['total_informes_act'] or 0) + (estadisticas['total_informes_tar'] or 0),
            'total_informes_actividad': estadisticas['total_informes_act'] or 0,
            'total_informes_tareas': estadisticas['total_informes_tar'] or 0,
            'total_tareas': estadisticas['total_tareas'] or 0
        }
    
    def calcular_porcentaje_ejecucion(self, ejecutado, presupuesto):
        """Calcula porcentaje de ejecución presupuestaria"""
        if presupuesto and presupuesto > 0:
            return round((ejecutado / presupuesto) * 100, 2)
        return 0.0