# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Count, Sum
from spme_monitoreo.models import SolicitudFondos
from spme_actividades.models import Actividad
from ..serializer.lista_sol_fondos_por_actividad_serializer import SolicitudFondosSimpleSerializer



class SolicitudesPorActividadConTareaNulaView(APIView):
    """
    Endpoint para obtener todas las solicitudes de fondos por idActividad
    FILTRADO: Solo las que tienen tarea_id = NULL
    """
    
    def get(self, request, id_actividad):
        """
        GET /api/actividades/{id_actividad}/solicitudes-sin-tarea/
        
        Parámetros opcionales:
        - estado: pendiente, validada, rechazada, etc.
        - fecha_desde: YYYY-MM-DD
        - fecha_hasta: YYYY-MM-DD
        - ordenar_por: fecha, monto, etc.
        """
        try:
            # 1. Verificar si la actividad existe
            try:
                actividad = Actividad.objects.get(id=id_actividad)
            except Actividad.DoesNotExist:
                return Response({
                    'success': False,
                    'error': f'Actividad con ID {id_actividad} no encontrada',
                    'actividad_id': id_actividad
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 2. Construir el queryset base con filtro de tarea nula
            queryset = SolicitudFondos.objects.filter(
                actividad_id=id_actividad,  # Filtrar por actividad
                tarea__isnull=True          # SOLO solicitudes SIN tarea
            )
            
            # 3. Aplicar filtros adicionales desde parámetros GET
            estado = request.query_params.get('estado')
            if estado:
                if estado == 'pendiente':
                    queryset = queryset.filter(
                        validacionResponsable=False,
                        validacionCoordinador=False
                    )
                elif estado == 'validada_parcial':
                    queryset = queryset.filter(
                        validacionResponsable=True,
                        validacionCoordinador=False
                    )
                elif estado == 'validada_completa':
                    queryset = queryset.filter(
                        validacionResponsable=True,
                        validacionCoordinador=True
                    )
                elif estado == 'rechazada':
                    queryset = queryset.filter(
                        validacionResponsable=False,
                        validacionCoordinador=True
                    )
            
            # Filtrar por rango de fechas
            fecha_desde = request.query_params.get('fecha_desde')
            fecha_hasta = request.query_params.get('fecha_hasta')
            
            if fecha_desde:
                queryset = queryset.filter(fechaSolicitud__gte=fecha_desde)
            if fecha_hasta:
                queryset = queryset.filter(fechaSolicitud__lte=fecha_hasta)
            
            # 4. Aplicar ordenamiento
            ordenar_por = request.query_params.get('ordenar_por', '-fechaSolicitud')
            
            # Validar campos de ordenamiento permitidos
            campos_permitidos = [
                'fechaSolicitud', '-fechaSolicitud',
                'montoSolicitado', '-montoSolicitado',
                'numeroFormulario', '-numeroFormulario',
                'fechaRealizacionActividad', '-fechaRealizacionActividad'
            ]
            
            if ordenar_por in campos_permitidos:
                queryset = queryset.order_by(ordenar_por)
            else:
                # Orden por defecto: más reciente primero
                queryset = queryset.order_by('-fechaSolicitud')
            
            # 5. Calcular estadísticas ANTES de la paginación
            total_solicitudes = queryset.count()
            
            estadisticas = {
                'total_solicitudes': total_solicitudes,
                'total_monto': queryset.aggregate(
                    total=Sum('montoSolicitado')
                )['total'] or 0,
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
            
            # 6. Paginación opcional
            pagina = request.query_params.get('pagina')
            por_pagina = request.query_params.get('por_pagina', 20)
            
            if pagina and por_pagina.isdigit():
                try:
                    pagina = int(pagina)
                    por_pagina = int(por_pagina)
                    
                    # Calcular límites
                    inicio = (pagina - 1) * por_pagina
                    fin = inicio + por_pagina
                    
                    # Obtener solicitudes paginadas
                    solicitudes_paginadas = list(queryset[inicio:fin])
                    total_paginas = (total_solicitudes + por_pagina - 1) // por_pagina
                    
                    # Serializar
                    serializer = SolicitudFondosSimpleSerializer(
                        solicitudes_paginadas, 
                        many=True
                    )
                    
                    return Response({
                        'success': True,
                        'actividad': {
                            'id': actividad.id,
                            'nombre': getattr(actividad, 'nombre', 'Actividad'),
                            'descripcion': getattr(actividad, 'descripcion', '')
                        },
                        'estadisticas': estadisticas,
                        'paginacion': {
                            'pagina_actual': pagina,
                            'por_pagina': por_pagina,
                            'total_solicitudes': total_solicitudes,
                            'total_paginas': total_paginas,
                            'mostrando': len(solicitudes_paginadas)
                        },
                        'filtros_aplicados': {
                            'tarea_nula': True,
                            'estado': estado,
                            'fecha_desde': fecha_desde,
                            'fecha_hasta': fecha_hasta,
                            'ordenar_por': ordenar_por
                        },
                        'solicitudes': serializer.data
                    }, status=status.HTTP_200_OK)
                    
                except (ValueError, IndexError):
                    # Si hay error en paginación, continuar sin paginar
                    pass
            
            # 7. Si no hay paginación o hay error, devolver todas
            serializer = SolicitudFondosSimpleSerializer(queryset, many=True)
            
            return Response({
                'success': True,
                'actividad': {
                    'id': actividad.id,
                    'nombre': getattr(actividad, 'nombre', 'Actividad'),
                    'descripcion': getattr(actividad, 'descripcion', '')
                },
                'estadisticas': estadisticas,
                'total_solicitudes': total_solicitudes,
                'filtros_aplicados': {
                    'tarea_nula': True,
                    'estado': estado,
                    'fecha_desde': fecha_desde,
                    'fecha_hasta': fecha_hasta,
                    'ordenar_por': ordenar_por
                },
                'solicitudes': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Error interno del servidor',
                'detalle': str(e),
                'actividad_id': id_actividad
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)