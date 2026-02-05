# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Count, Sum, DecimalField
from django.db.models.functions import Coalesce
from spme_monitoreo.models import SolicitudViajeActPei
from spme_actividades.models import ActividadPei, TareaActividadPei
from ..serializer.lista_sol_viaje_por_actividad_pei_views import SolicitudViajeActPeiSimpleSerializer

class SolicitudesViajePorActividadPeiConTareaNulaView(APIView):
    """
    Endpoint para obtener todas las solicitudes de viaje (SolicitudViajeActPei) 
    por id_actividad_pei
    FILTRADO: Solo las que tienen tarea_id = NULL
    """
    
    def get(self, request, id_actividad_pei):
        """
        GET /api/solicitudes-viaje/actividad-pei/{id_actividad_pei}/sin-tarea/
        
        Parámetros opcionales:
        - estado: pendiente, validada_parcial, validada_completa, rechazada
        - fecha_desde: YYYY-MM-DD (fechaSolicitud)
        - fecha_hasta: YYYY-MM-DD (fechaSolicitud)
        - evento: búsqueda por nombre de evento
        - ordenar_por: fechaSolicitud, montoSolicitado, numeroFormulario, fechaEvento, etc.
        - pagina: número de página
        - por_pagina: elementos por página (default: 20)
        """
        try:
            # 1. Verificar si la actividad PEI existe
            try:
                actividad_pei = ActividadPei.objects.get(id=id_actividad_pei)
            except ActividadPei.DoesNotExist:
                return Response({
                    'success': False,
                    'error': f'Actividad PEI con ID {id_actividad_pei} no encontrada',
                    'actividad_pei_id': id_actividad_pei
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 2. Construir el queryset base con filtro de tarea nula
            queryset = SolicitudViajeActPei.objects.filter(
                actividad_id=id_actividad_pei,  # Filtrar por actividad PEI
                tarea__isnull=True              # SOLO solicitudes SIN tarea
            ).select_related(
                'actividad', 
                'tarea', 
                'formaPago', 
                'usuario', 
                'responsable', 
                'coordinador'
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
            
            # Filtrar por rango de fechas (fecha de solicitud)
            fecha_desde = request.query_params.get('fecha_desde')
            fecha_hasta = request.query_params.get('fecha_hasta')
            
            if fecha_desde:
                queryset = queryset.filter(fechaSolicitud__gte=fecha_desde)
            if fecha_hasta:
                queryset = queryset.filter(fechaSolicitud__lte=fecha_hasta)
            
            # Filtrar por rango de fechas del evento
            fecha_evento_desde = request.query_params.get('fecha_evento_desde')
            fecha_evento_hasta = request.query_params.get('fecha_evento_hasta')
            
            if fecha_evento_desde:
                queryset = queryset.filter(fechaEvento__gte=fecha_evento_desde)
            if fecha_evento_hasta:
                queryset = queryset.filter(fechaEvento__lte=fecha_evento_hasta)
            
            # Filtrar por número de formulario o evento (búsqueda parcial)
            busqueda = request.query_params.get('busqueda')
            if busqueda:
                queryset = queryset.filter(
                    Q(numeroFormulario__icontains=busqueda) |
                    Q(evento__icontains=busqueda) |
                    Q(lugarEvento__icontains=busqueda) |
                    Q(organizador__icontains=busqueda)
                )
            
            # Filtrar por lugar del evento
            lugar_evento = request.query_params.get('lugar_evento')
            if lugar_evento:
                queryset = queryset.filter(lugarEvento__icontains=lugar_evento)
            
            # 4. Aplicar ordenamiento
            ordenar_por = request.query_params.get('ordenar_por', '-fechaSolicitud')
            
            # Validar campos de ordenamiento permitidos
            campos_permitidos = [
                'id', '-id',
                'fechaSolicitud', '-fechaSolicitud',
                'fechaEvento', '-fechaEvento',
                'montoSolicitado', '-montoSolicitado',
                'numeroFormulario', '-numeroFormulario',
                'evento', '-evento',
                'lugarEvento', '-lugarEvento',
                'validacionResponsable', '-validacionResponsable',
                'validacionCoordinador', '-validacionCoordinador'
            ]
            
            if ordenar_por in campos_permitidos:
                queryset = queryset.order_by(ordenar_por)
            else:
                # Orden por defecto: más reciente primero
                queryset = queryset.order_by('-fechaSolicitud')
            
            # 5. Calcular estadísticas
            total_solicitudes = queryset.count()
            
            # Calcular total de montos por estado
            total_monto = queryset.aggregate(
                total=Coalesce(Sum('montoSolicitado'), 0, output_field=DecimalField())
            )['total']
            
            # Contar por estado de validación
            pendientes_count = queryset.filter(
                validacionResponsable=False,
                validacionCoordinador=False
            ).count()
            
            validadas_parcial_count = queryset.filter(
                validacionResponsable=True,
                validacionCoordinador=False
            ).count()
            
            validadas_completa_count = queryset.filter(
                validacionResponsable=True,
                validacionCoordinador=True
            ).count()
            
            rechazadas_count = queryset.filter(
                validacionResponsable=False,
                validacionCoordinador=True
            ).count()
            
            estadisticas = {
                'total_solicitudes': total_solicitudes,
                'total_monto': float(total_monto),
                'por_estado': {
                    'pendientes': pendientes_count,
                    'validadas_parcialmente': validadas_parcial_count,
                    'validadas_completamente': validadas_completa_count,
                    'rechazadas': rechazadas_count
                }
            }
            
            # 6. Información de la actividad PEI
            actividad_info = {
                'id': actividad_pei.id,
                'codigo': actividad_pei.codigo,
                'nombre_corto': actividad_pei.nombreCorto,
                'descripcion': actividad_pei.descripcion,
                'estado': actividad_pei.estado,
                'estado_display': actividad_pei.get_estado_display(),
                'fecha_inicio': actividad_pei.fecha_inicio,
                'fecha_cierre': actividad_pei.fecha_cierre,
                'presupuesto': float(actividad_pei.presupuesto) if actividad_pei.presupuesto else 0,
                'presupuesto_global': float(actividad_pei.presupuestoGlobal) if actividad_pei.presupuestoGlobal else 0,
                'total_ejecutado': float(actividad_pei.totalEjecutado) if actividad_pei.totalEjecutado else 0,
                'saldo': float(actividad_pei.saldo) if actividad_pei.saldo else 0,
                'grado_ejecucion': actividad_pei.gradoEjecucion,
                'responsable': {
                    'id': actividad_pei.responsable.id if actividad_pei.responsable else None,
                    'nombre': actividad_pei.responsable.get_full_name() if actividad_pei.responsable else None
                }
            }
            
            # 7. Paginación
            pagina = request.query_params.get('pagina')
            por_pagina = request.query_params.get('por_pagina', '20')
            
            if pagina and por_pagina and por_pagina.isdigit():
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
                    serializer = SolicitudViajeActPeiSimpleSerializer(
                        solicitudes_paginadas, 
                        many=True,
                        context={'request': request}
                    )
                    
                    return Response({
                        'success': True,
                        'actividad_pei': actividad_info,
                        'estadisticas': estadisticas,
                        'paginacion': {
                            'pagina_actual': pagina,
                            'por_pagina': por_pagina,
                            'total_solicitudes': total_solicitudes,
                            'total_paginas': total_paginas,
                            'mostrando': len(solicitudes_paginadas),
                            'inicio': inicio + 1 if total_solicitudes > 0 else 0,
                            'fin': min(fin, total_solicitudes)
                        },
                        'filtros_aplicados': {
                            'tarea_nula': True,
                            'estado': estado,
                            'fecha_desde': fecha_desde,
                            'fecha_hasta': fecha_hasta,
                            'fecha_evento_desde': fecha_evento_desde,
                            'fecha_evento_hasta': fecha_evento_hasta,
                            'busqueda': busqueda,
                            'lugar_evento': lugar_evento,
                            'ordenar_por': ordenar_por
                        },
                        'solicitudes_viaje': serializer.data
                    }, status=status.HTTP_200_OK)
                    
                except (ValueError, IndexError) as e:
                    # Si hay error en paginación, continuar sin paginar
                    print(f"Error en paginación: {e}")
                    pass
            
            # 8. Si no hay paginación o hay error, devolver todas
            serializer = SolicitudViajeActPeiSimpleSerializer(
                queryset, 
                many=True,
                context={'request': request}
            )
            
            return Response({
                'success': True,
                'actividad_pei': actividad_info,
                'estadisticas': estadisticas,
                'total_solicitudes': total_solicitudes,
                'filtros_aplicados': {
                    'tarea_nula': True,
                    'estado': estado,
                    'fecha_desde': fecha_desde,
                    'fecha_hasta': fecha_hasta,
                    'fecha_evento_desde': fecha_evento_desde,
                    'fecha_evento_hasta': fecha_evento_hasta,
                    'busqueda': busqueda,
                    'lugar_evento': lugar_evento,
                    'ordenar_por': ordenar_por
                },
                'solicitudes_viaje': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            return Response({
                'success': False,
                'error': 'Error interno del servidor',
                'detalle': str(e),
                'traceback': traceback.format_exc(),
                'actividad_pei_id': id_actividad_pei
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SolicitudesViajePorTareaActividadPeiView(APIView):
    """
    Endpoint para obtener solicitudes de viaje por tarea de ActividadPei
    """
    
    def get(self, request, id_tarea_pei):
        """
        GET /api/solicitudes-viaje/tarea-actividad-pei/{id_tarea_pei}/
        """
        try:
            # Verificar si la tarea PEI existe
            try:
                tarea_pei = TareaActividadPei.objects.get(id=id_tarea_pei)
            except TareaActividadPei.DoesNotExist:
                return Response({
                    'success': False,
                    'error': f'Tarea Actividad PEI con ID {id_tarea_pei} no encontrada',
                    'tarea_pei_id': id_tarea_pei
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Obtener solicitudes relacionadas con esta tarea
            queryset = SolicitudViajeActPei.objects.filter(
                tarea_id=id_tarea_pei
            ).select_related(
                'actividad', 
                'tarea', 
                'formaPago', 
                'usuario', 
                'responsable', 
                'coordinador'
            )
            
            # Aplicar ordenamiento
            ordenar_por = request.query_params.get('ordenar_por', '-fechaSolicitud')
            if ordenar_por in ['fechaSolicitud', '-fechaSolicitud', 'montoSolicitado', '-montoSolicitado', 'fechaEvento', '-fechaEvento']:
                queryset = queryset.order_by(ordenar_por)
            
            # Serializar
            serializer = SolicitudViajeActPeiSimpleSerializer(
                queryset, 
                many=True,
                context={'request': request}
            )
            
            # Información de la tarea PEI
            tarea_info = {
                'id': tarea_pei.id,
                'codigo': tarea_pei.codigo,
                'titulo': tarea_pei.titulo,
                'descripcion': tarea_pei.descripcion,
                'estado': tarea_pei.estado,
                'estado_display': tarea_pei.get_estado_display(),
                'fecha_creacion': tarea_pei.fecha_creacion,
                'fecha_ejecucion': tarea_pei.fecha_ejecucion,
                'fecha_limite': tarea_pei.fecha_limite,
                'presupuesto': float(tarea_pei.presupuesto) if tarea_pei.presupuesto else 0,
                'actividad_pei': {
                    'id': tarea_pei.actividad.id if tarea_pei.actividad else None,
                    'codigo': tarea_pei.actividad.codigo if tarea_pei.actividad else None,
                    'nombre_corto': tarea_pei.actividad.nombreCorto if tarea_pei.actividad else None
                }
            }
            
            # Calcular estadísticas
            total_monto = queryset.aggregate(
                total=Coalesce(Sum('montoSolicitado'), 0, output_field=DecimalField())
            )['total']
            
            return Response({
                'success': True,
                'tarea_pei': tarea_info,
                'estadisticas': {
                    'total_solicitudes': queryset.count(),
                    'total_monto': float(total_monto)
                },
                'solicitudes_viaje': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            return Response({
                'success': False,
                'error': 'Error interno del servidor',
                'detalle': str(e),
                'traceback': traceback.format_exc(),
                'tarea_pei_id': id_tarea_pei
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)