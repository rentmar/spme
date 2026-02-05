# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Sum, DecimalField
from django.db.models.functions import Coalesce
from spme_monitoreo.models import RendicionCuentasActPei
from spme_actividades.models import ActividadPei
from ..serializer.lista_rendicion_cuentas_por_actividad_pei_serializer import RendicionCuentasActPeiSerializer


class RendicionesCuentasPorActividadPeiSinTareaView(APIView):
    """
    Endpoint para obtener rendiciones de cuentas 
    por actividad PEI con tarea_id = NULL
    """
    
    def get(self, request, id_actividad_pei):
        """
        GET /api/rendiciones-cuentas/actividad-pei/{id_actividad_pei}/sin-tarea/
        """
        try:
            # 1. Verificar si la actividad PEI existe
            try:
                actividad_pei = ActividadPei.objects.get(id=id_actividad_pei)
            except ActividadPei.DoesNotExist:
                return Response({
                    'success': False,
                    'error': f'Actividad PEI con ID {id_actividad_pei} no encontrada'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 2. Construir el queryset base con filtro de tarea nula
            queryset = RendicionCuentasActPei.objects.filter(
                actividad_id=id_actividad_pei,
                tarea__isnull=True
            ).select_related(
                'actividad', 'tarea', 'usuario', 'responsable', 
                'coordinador', 'contador', 'administrador',
                'solicitudFondos', 'solicitudReembolso', 
                'solicitudViaje', 'solicitudPagoDirecto'
            )
            
            # 3. Aplicar filtros adicionales
            estado = request.query_params.get('estado')
            if estado:
                if estado == 'pendiente':
                    queryset = queryset.filter(
                        validacionResponsable=False,
                        validacionCoordinador=False,
                        validacionContador=False,
                        validacionAdministrador=False
                    )
                elif estado == 'validada_responsable':
                    queryset = queryset.filter(
                        validacionResponsable=True,
                        validacionCoordinador=False,
                        validacionContador=False,
                        validacionAdministrador=False
                    )
                elif estado == 'validada_parcial':
                    queryset = queryset.filter(
                        validacionResponsable=True,
                        validacionCoordinador=True,
                        validacionContador=False,
                        validacionAdministrador=False
                    )
                elif estado == 'validada_contador':
                    queryset = queryset.filter(
                        validacionResponsable=True,
                        validacionCoordinador=True,
                        validacionContador=True,
                        validacionAdministrador=False
                    )
                elif estado == 'validada_completa':
                    queryset = queryset.filter(
                        validacionResponsable=True,
                        validacionCoordinador=True,
                        validacionContador=True,
                        validacionAdministrador=True
                    )
            
            # Filtrar por rango de fechas de rendición
            fecha_desde = request.query_params.get('fecha_desde')
            fecha_hasta = request.query_params.get('fecha_hasta')
            
            if fecha_desde:
                queryset = queryset.filter(fechaRendicion__gte=fecha_desde)
            if fecha_hasta:
                queryset = queryset.filter(fechaRendicion__lte=fecha_hasta)
            
            # Filtrar por rango de fechas de actividad
            fecha_actividad_desde = request.query_params.get('fecha_actividad_desde')
            fecha_actividad_hasta = request.query_params.get('fecha_actividad_hasta')
            
            if fecha_actividad_desde:
                queryset = queryset.filter(fechaActividad__gte=fecha_actividad_desde)
            if fecha_actividad_hasta:
                queryset = queryset.filter(fechaActividad__lte=fecha_actividad_hasta)
            
            # Búsqueda general
            busqueda = request.query_params.get('busqueda')
            if busqueda:
                queryset = queryset.filter(
                    Q(numeroFormulario__icontains=busqueda) |
                    Q(cpteDiario__icontains=busqueda) |
                    Q(descripcionActividad__icontains=busqueda)
                )
            
            # 4. Aplicar ordenamiento
            ordenar_por = request.query_params.get('ordenar_por', '-fechaRendicion')
            campos_permitidos = [
                'fechaRendicion', '-fechaRendicion',
                'fechaActividad', '-fechaActividad',
                'fechaDesembolso', '-fechaDesembolso',
                'montoAsignado', '-montoAsignado',
                'montoDescargado', '-montoDescargado',
                'numeroFormulario', '-numeroFormulario'
            ]
            
            if ordenar_por in campos_permitidos:
                queryset = queryset.order_by(ordenar_por)
            else:
                queryset = queryset.order_by('-fechaRendicion')
            
            # 5. Calcular estadísticas
            total_rendiciones = queryset.count()
            
            total_monto_asignado = queryset.aggregate(
                total=Coalesce(Sum('montoAsignado'), 0, output_field=DecimalField())
            )['total'] or 0
            
            total_monto_descargado = queryset.aggregate(
                total=Coalesce(Sum('montoDescargado'), 0, output_field=DecimalField())
            )['total'] or 0
            
            total_saldo = queryset.aggregate(
                total=Coalesce(Sum('saldo'), 0, output_field=DecimalField())
            )['total'] or 0
            
            estadisticas = {
                'total_rendiciones': total_rendiciones,
                'total_monto_asignado': float(total_monto_asignado),
                'total_monto_descargado': float(total_monto_descargado),
                'total_saldo': float(total_saldo),
                'por_estado': {
                    'pendientes': queryset.filter(
                        validacionResponsable=False,
                        validacionCoordinador=False,
                        validacionContador=False,
                        validacionAdministrador=False
                    ).count(),
                    'validadas_responsable': queryset.filter(
                        validacionResponsable=True,
                        validacionCoordinador=False,
                        validacionContador=False,
                        validacionAdministrador=False
                    ).count(),
                    'validadas_parcialmente': queryset.filter(
                        validacionResponsable=True,
                        validacionCoordinador=True,
                        validacionContador=False,
                        validacionAdministrador=False
                    ).count(),
                    'validadas_contador': queryset.filter(
                        validacionResponsable=True,
                        validacionCoordinador=True,
                        validacionContador=True,
                        validacionAdministrador=False
                    ).count(),
                    'validadas_completamente': queryset.filter(
                        validacionResponsable=True,
                        validacionCoordinador=True,
                        validacionContador=True,
                        validacionAdministrador=True
                    ).count()
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
            
            # 7. Serializar
            serializer = RendicionCuentasActPeiSerializer(queryset, many=True)
            
            return Response({
                'success': True,
                'actividad_pei': actividad_info,
                'estadisticas': estadisticas,
                'total_rendiciones': total_rendiciones,
                'filtros_aplicados': {
                    'tarea_nula': True,
                    'estado': estado,
                    'fecha_desde': fecha_desde,
                    'fecha_hasta': fecha_hasta,
                    'fecha_actividad_desde': fecha_actividad_desde,
                    'fecha_actividad_hasta': fecha_actividad_hasta,
                    'busqueda': busqueda,
                    'ordenar_por': ordenar_por
                },
                'rendiciones_cuentas': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Error interno del servidor',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)