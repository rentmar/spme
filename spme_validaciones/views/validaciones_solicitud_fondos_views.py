#spme/spme_validaciones/views/validaciones_solicitud_fondos_views.py
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

#models
from spme_monitoreo.models import SolicitudFondos
from spme_autenticacion.models import Usuario
from ..models import ValidacionSolicitudFondos

#Serializer - Sol de Fondos
from ..serializers.validaciones_solicitud_fondos_serializers import (
    ValidacionSolicitudFondosSerializer,
    AsignarValidadoresSolicitudFondosSerializer,
    ResetearValidacionesSolicitudFondosSerializer,
)

#Services - Sol de Fondos
from ..services.validacion_solicitud_fondos_service import ValidacionSolicitudFondosService
#Repositories - SOl de Fondos
from ..repositories.validacion_solicitud_fondos_repository import ValidacionSolicitudFondosRepository

#Serializer Emitir Voto y Reset
from ..serializers.validaciones_informes_actividad_subac_serializers import (
    EmitirVotoSerializer,
    HistorialValidacionSerializer,
)

#Services - mensajes
from spme_mensajes.services.notificacion_service import (
    crear_mensajes_validacion_solicitud_fondos,
    crear_mensaje_solicitud_aprobada,
    crear_mensaje_solicitud_rechazada,
) 

#Notificaciones email
from spme_monitor_estados.utils.encolar import (
    encolar_validacion_pendiente,
    encolar_validacion_aprobada,
    encolar_validacion_rechazada,
    encolar_confirmacion_validador,
    encolar_validacion_pendiente_sf,
)

import logging

logger = logging.getLogger(__name__)
repo = ValidacionSolicitudFondosRepository()


# ===================================================================
# ASIGNAR VALIDADORES
# ===================================================================
class AsignarValidadoresSolicitudFondosViewSet(viewsets.ViewSet):
    """
    POST /api/solicitud-fondos/{id}/asignar-validadores/ 
    - Payload: {"validador_ids": [2,3]}
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create(self, request, solicitud_id=None):
        serializer = AsignarValidadoresSolicitudFondosSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        solicitud = get_object_or_404(SolicitudFondos, id=solicitud_id)
        validadores = Usuario.objects.filter(
            id__in=serializer.validated_data['validador_ids']
        )

        if len(validadores) != len(serializer.validated_data['validador_ids']):
            ids_encontrados = list(validadores.values_list('id', flat=True))
            ids_faltantes = set(serializer.validated_data['validador_ids']) - set(ids_encontrados)
            return Response(
                {'error': f'Validadores no encontrados: {list(ids_faltantes)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resultados, errores, validadores_json = [], [], []

        for validador in validadores:
            try:
                if repo.existe_validador(solicitud.id, 'solicitud', validador.id):
                    errores.append({
                        'validador_id': validador.id,
                        'error': f'Ya existe validación para {validador.get_full_name()}'
                    })
                    continue
                
                v = repo.crear(
                    solicitud=solicitud,
                    usuarioValidador=validador,
                    usuarioRedactor=request.user,
                    estado='PENDIENTE',
                    versionDocumento='1'
                )
                resultados.append(ValidacionSolicitudFondosSerializer(v).data)
                validadores_json.append({
                    'id': validador.id,
                    'nombre_completo': validador.get_full_name(),
                    'rol': validador.cargo or 'validador',
                    'estado': 'PENDIENTE',
                    'fechaAsignacion': str(timezone.now())
                })
                
            except ValidationError as e:
                errores.append({'validador_id': validador.id, 'error': str(e)})
            except Exception as e:
                errores.append({'validador_id': validador.id, 'error': str(e)})
        
        # NOTIFICACIONES (si falla, rollback de toda la transacción)
        if validadores_json:
            crear_mensajes_validacion_solicitud_fondos(solicitud, validadores_json)
            for val in validadores:
                encolar_validacion_pendiente_sf(
                    solicitud=solicitud,
                    validador=val,
                    enlace_ver_detalle=f"/solicitudes-fondos/{solicitud.id}/validar"
                )
        return Response({
            'mensaje': f'Creadas {len(resultados)} validaciones',
            'errores': errores if errores else None,
            'resultados': resultados
        }, status=status.HTTP_201_CREATED)
        
        
        
        

class VotarSolicitudFondosViewSet(viewsets.ViewSet):
    """
    POST /api/solicitud-fondos/{id}/votar/
    """
    def create(self, request, solicitud_id=None):
        return Response({'msg':'Votar Sol de FOndos'})


class ResetearValidacionesSolicitudFondosViewSet(viewsets.ViewSet):
    """
    POST /api/solicitud-fondos/{id}/resetear-validaciones/
    """
    def create(self, request, solicitud_id=None):
        return Response({'msg':'reset Sol de FOndos'})
    
# ===================================================================
# ESTADO DE VALIDACIÓN
# ===================================================================
class EstadoValidacionSolicitudFondosAPIView(APIView):
    """
    GET /api/solicitud-fondos/{solicitud_id}/estado-validacion/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, solicitud_id):
        solicitud = get_object_or_404(SolicitudFondos, id=solicitud_id)
        estadisticas = repo.obtener_estadisticas_por_solicitud(solicitud_id)

        #Tipo de solicitud
        if solicitud.actividad_id and not solicitud.tarea_id:
            tipo = 'ACTIVIDAD'
        elif solicitud.actividad_id and solicitud.tarea_id:
            tipo = 'TAREA'
        else:
            tipo = 'GENERAL'

        return Response({
            'solicitud_id': solicitud.id,
            'solicitud_codigo': solicitud.numeroFormulario or f"SF-{solicitud.id}",
            'monto': str(solicitud.montoSolicitado),
            'tipo_solicitud': tipo,
            **estadisticas
        }, status=status.HTTP_200_OK)
    
# ===================================================================
# HISTORIAL
# ===================================================================
class HistorialValidacionSolicitudFondosAPIView(APIView):
    """
    GET /api/solicitud-fondos/{solicitud_id}/historial/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, solicitud_id):
        solicitud = get_object_or_404(SolicitudFondos, id=solicitud_id)

        from ..models import HistorialValidacion
        historial = HistorialValidacion.objects.filter(
            validacion__validacionsolicitudfondos__solicitud=solicitud
        ).select_related('usuario', 'validacion__validacionsolicitudfondos').order_by('-fechaCambio')

        serializer = HistorialValidacionSerializer(historial, many=True)

        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        }, status=status.HTTP_200_OK)

# ===================================================================
# MIS VALIDACIONES PENDIENTES 
# Solicitud de Fondos
# ===================================================================
class MisValidacionesPendientesSolicitudFondosAPIView(APIView):
    """
    GET /api/solicitud-fondos/mis-pendientes/
    Return: Todas las validaciones para solicitud de fondo pendientes
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        validaciones = repo.obtener_por_validador_con_solicitud(request.user.id)
        pendientes = [v for v in validaciones if v.estado == 'PENDIENTE']

        data = []
        
        for v in pendientes:
            data.append({
                'validacion_id': v.id,
                'codigo_seguimiento': v.codigoSeguimiento,
                'estado': v.estado,
                'fecha_asignacion': v.fechaAsignacion,
                'solicitud_id': v.solicitud.id,
                'solicitud_codigo': v.solicitud.numeroFormulario or f"SF-{v.solicitud.id}",
                'solicitud_monto': str(v.solicitud.montoSolicitado),
                'solicitante_nombre': v.usuarioRedactor.get_full_name() if v.usuarioRedactor else 'N/A',
                'tipo_solicitud': v.tipo_solicitud,
            })
        
        return Response({
            'count': len(data),
            'results': data
        }, status=status.HTTP_200_OK)



