# views.py (en la misma carpeta)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404
from spme_monitoreo.models import RendicionCuentas
from spme_actividades.models import Actividad
from ..serializer.lista_rendicion_cuentas_por_actividad_serializer import RendicionCuentasSimpleSerializer


class RendicionesSinTareaPorActividadView(APIView):
    """
    Endpoint para obtener todas las RENDICIONES DE CUENTAS por idActividad
    FILTRADO: Solo las que tienen tarea_id = NULL
    """
    
    def get(self, request, id_actividad):
        """
        GET /api/actividades/{id_actividad}/rendiciones-sin-tarea/
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
            queryset = RendicionCuentas.objects.filter(
                actividad_id=id_actividad,  # Filtrar por actividad
                tarea__isnull=True          # SOLO rendiciones SIN tarea
            )
            
            # 3. Aplicar filtros adicionales desde parámetros GET
            estado = request.query_params.get('estado')
            if estado:
                if estado == 'pendiente':
                    queryset = queryset.filter(
                        validacionResponsable=False,
                        validacionCoordinador=False,
                        validacionContador=False,
                        validacionAdministrador=False
                    )
                elif estado == 'validada_parcial':
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
                elif estado == 'validada_completa':
                    queryset = queryset.filter(
                        validacionResponsable=True,
                        validacionCoordinador=True,
                        validacionContador=True,
                        validacionAdministrador=True
                    )
            
            # Filtrar por rango de fechas
            fecha_desde = request.query_params.get('fecha_desde')
            fecha_hasta = request.query_params.get('fecha_hasta')
            
            if fecha_desde:
                queryset = queryset.filter(fechaRendicion__gte=fecha_desde)
            if fecha_hasta:
                queryset = queryset.filter(fechaRendicion__lte=fecha_hasta)
            
            # 4. Aplicar ordenamiento
            ordenar_por = request.query_params.get('ordenar_por', '-fechaRendicion')
            
            # Validar campos de ordenamiento permitidos
            campos_permitidos = [
                'fechaRendicion', '-fechaRendicion',
                'fechaDesembolso', '-fechaDesembolso',
                'montoAsignado', '-montoAsignado',
                'montoDescargado', '-montoDescargado',
                'numeroFormulario', '-numeroFormulario'
            ]
            
            if ordenar_por in campos_permitidos:
                queryset = queryset.order_by(ordenar_por)
            else:
                # Orden por defecto: más reciente primero
                queryset = queryset.order_by('-fechaRendicion')
            
            # 5. Calcular estadísticas (adaptadas para rendiciones)
            total_rendiciones = queryset.count()
            
            estadisticas = {
                'total_rendiciones': total_rendiciones,
                'total_monto_asignado': queryset.aggregate(
                    total=Sum('montoAsignado')
                )['total'] or 0,
                'total_monto_descargado': queryset.aggregate(
                    total=Sum('montoDescargado')
                )['total'] or 0,
                'total_saldo': queryset.aggregate(
                    total=Sum('saldo')
                )['total'] or 0,
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
                    
                    # Obtener rendiciones paginadas
                    rendiciones_paginadas = list(queryset[inicio:fin])
                    total_paginas = (total_rendiciones + por_pagina - 1) // por_pagina
                    
                    # Serializar
                    serializer = RendicionCuentasSimpleSerializer(
                        rendiciones_paginadas, 
                        many=True
                    )
                    
                    return Response({
                        'success': True,
                        'actividad': {
                            'id': actividad.id,
                            'nombre': actividad.nombreCorto,
                            'descripcion': actividad.descripcion,
                            'codigo': actividad.codigo
                        },
                        'estadisticas': estadisticas,
                        'paginacion': {
                            'pagina_actual': pagina,
                            'por_pagina': por_pagina,
                            'total_rendiciones': total_rendiciones,
                            'total_paginas': total_paginas,
                            'mostrando': len(rendiciones_paginadas)
                        },
                        'filtros_aplicados': {
                            'tarea_nula': True,
                            'estado': estado,
                            'fecha_desde': fecha_desde,
                            'fecha_hasta': fecha_hasta,
                            'ordenar_por': ordenar_por
                        },
                        'rendiciones': serializer.data  # Cambiado de 'solicitudes' a 'rendiciones'
                    }, status=status.HTTP_200_OK)
                    
                except (ValueError, IndexError):
                    # Si hay error en paginación, continuar sin paginar
                    pass
            
            # 7. Si no hay paginación o hay error, devolver todas
            serializer = RendicionCuentasSimpleSerializer(queryset, many=True)
            
            return Response({
                'success': True,
                'actividad': {
                    'id': actividad.id,
                    'nombre': actividad.nombreCorto,
                    'descripcion': actividad.descripcion,
                    'codigo': actividad.codigo
                },
                'estadisticas': estadisticas,
                'total_rendiciones': total_rendiciones,
                'filtros_aplicados': {
                    'tarea_nula': True,
                    'estado': estado,
                    'fecha_desde': fecha_desde,
                    'fecha_hasta': fecha_hasta,
                    'ordenar_por': ordenar_por
                },
                'rendiciones': serializer.data  # Cambiado de 'solicitudes' a 'rendiciones'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Error interno del servidor',
                'detalle': str(e),
                'actividad_id': id_actividad
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)