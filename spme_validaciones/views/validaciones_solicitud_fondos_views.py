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
    

class EstadoValidacionSolicitudFondosAPIView(APIView):
    """
    GET /api/solicitud-fondos/{id}/estado-validacion/
    """
    def get(self, request, solicitud_id):
        return Response({'msg':'Estado validacion Sol de FOndos'})
    

class HistorialValidacionSolicitudFondosAPIView(APIView):
    """
    GET /api/solicitud-fondos/{id}/historial/
    """
    # permission_classes = [IsAuthenticated]
    
    def get(self, request, solicitud_id):
        return Response({'msg':'Historial validacion Sol de FOndos'})

class MisValidacionesPendientesSolicitudFondosAPIView(APIView):
    """
    GET /api/solicitud-fondos/mis-pendientes/
    """
    # permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'msg':'Mis validaciones pendientes Sol de Fondos'})
    



