from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

# Models
from spme_monitoreo.models import SolicitudReembolso
from spme_autenticacion.models import Usuario
from ..models import ValidacionSolicitudReembolso

# Serializers
from ..serializers.validaciones_solicitud_reembolso_serializers import (
    ValidacionSolicitudReembolsoSerializer,
    AsignarValidadoresSolicitudReembolsoSerializer,
    ResetearValidacionesSolicitudReembolsoSerializer,
)

# Services
from ..services.validacion_solicitud_reembolso_service import ValidacionSolicitudReembolsoService

# Repositories
from ..repositories.validacion_solicitud_reembolso_repository import ValidacionSolicitudReembolsoRepository

# Serializer Emitir Voto y Historial
from ..serializers.validaciones_informes_actividad_subac_serializers import (
    EmitirVotoSerializer,
    HistorialValidacionSerializer,
)

# Services - mensajes
from spme_mensajes.services.notificacion_service import (
    crear_mensajes_validacion_solicitud_fondos,
    crear_mensaje_solicitud_aprobada,
    crear_mensaje_solicitud_rechazada,
    crear_mensaje_revision_solicitud_fondos,
)

# Notificaciones email
from spme_monitor_estados.utils.encolar import (
    encolar_validacion_pendiente_sf,
    encolar_validacion_aprobada_sf,
    encolar_validacion_rechazada_sf,
    encolar_confirmacion_validador_sf,
    encolar_revision_solicitud_fondos,
)


#Notificacion email - celery
from spme_email.services.notificacion_service import NotificacionService
#Notificacion via mensajeria interna
from spme_mensajes.services.notificacion_service import enviar_notificacion_mensajeria_interna

import logging

logger = logging.getLogger(__name__)
repo = ValidacionSolicitudReembolsoRepository()


# ===================================================================
# ASIGNAR VALIDADORES
# ===================================================================
class AsignarValidadoresSolicitudReembolsoViewSet(viewsets.ViewSet):
    """
    POST /api/solicitud-reembolso/{id}/asignar-validadores/ 
    - Payload: {"validador_ids": [2,3]}
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        self.servicio = NotificacionService()

    @transaction.atomic
    def create(self, request, solicitud_id=None):
        serializer = AsignarValidadoresSolicitudReembolsoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        solicitud = get_object_or_404(SolicitudReembolso, id=solicitud_id)
        validadores = Usuario.objects.filter(
            id__in=serializer.validated_data['validador_ids']
        )
        destinatariosIds = serializer.validated_data['validador_ids']

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
                resultados.append(ValidacionSolicitudReembolsoSerializer(v).data)
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
        
        if validadores_json:
            # crear_mensajes_validacion_solicitud_fondos(solicitud, validadores_json)
            # for val in validadores:
            #     encolar_validacion_pendiente_sf(
            #         solicitud=solicitud,
            #         validador=val,
            #         enlace_ver_detalle=f"/solicitudes-reembolso/{solicitud.id}/validar"
            #     )
            respmensaje = enviar_notificacion_mensajeria_interna(
                'reposicion', 
                'revision',
                solicitud,
                destinatariosIds,
                request.headers.get('Origin', '')
            )

            resultadoEnvio = self.servicio.enviar(
                'reposicion',
                solicitud.id, 
                'revision', 
                destinatariosIds, 
                request.headers.get('Origin', '')
            )
            
        return Response({
            'mensaje': f'Creadas {len(resultados)} validaciones',
            'errores': errores if errores else None,
            'resultados': resultados
        }, status=status.HTTP_201_CREATED)


# ===================================================================
# EMITIR VOTO
# ===================================================================
class VotarSolicitudReembolsoViewSet(viewsets.ViewSet):
    """
    POST /api/solicitud-reembolso/{solicitud_id}/votar/
    Payload: {"validacion_id": 15, "estado": "APROBADO", "comentarios": "..."}
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        self.servicio = NotificacionService()

    @transaction.atomic
    def create(self, request, solicitud_id=None):
        voto_serializer = EmitirVotoSerializer(data=request.data)
        if not voto_serializer.is_valid():
            return Response(voto_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validacion_id = request.data.get('validacion_id')
        voto = voto_serializer.validated_data['estado']
        comentarios = voto_serializer.validated_data.get('comentarios', '')

        if voto == 'RECHAZADO' and not comentarios:
            return Response(
                {'error': 'Los comentarios son obligatorios cuando se rechaza'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            validacion = ValidacionSolicitudReembolso.objects.get(
                id=validacion_id,
                usuarioValidador=request.user,
                estado='PENDIENTE'
            )
        except ValidacionSolicitudReembolso.DoesNotExist:
            return Response(
                {'error': 'Validación no encontrada o ya procesada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        validacion.estado = voto
        validacion.comentarios = comentarios
        validacion.save()
        
        solicitud = validacion.solicitud
        context = solicitud.get_mensaje_contexto()
        solicitante_id = context['solicitante_id']
        destinatarios_ids = [solicitante_id]

        encolar_confirmacion_validador_sf(
            solicitud=solicitud,
            validador=request.user,
            accion=voto.lower()
        )

        if voto == 'APROBADO':
            resumen = repo.obtener_resumen_estado_solicitud(solicitud.id)
            if resumen['aprobado_totalmente']:
                # validaciones_aprobadas = ValidacionSolicitudReembolso.objects.filter(
                #     solicitud=solicitud, estado='APROBADO'
                # )
                # crear_mensaje_solicitud_aprobada(solicitud, validaciones_aprobadas)
                # encolar_validacion_aprobada_sf(
                #     solicitud=solicitud,
                #     validador=request.user
                # )

                #Agregar la notificacion al 3er usuario
                destinatarios_ids.append(57)
                destinatarios_ids = list(set(destinatarios_ids))
                logger.info(f"Destinatarios de aprobación: {destinatarios_ids}")


                respmensaje = enviar_notificacion_mensajeria_interna(
                    'reposicion', 
                    'aprobacion',
                    solicitud,
                    destinatarios_ids,
                    request.headers.get('Origin', '')
                )

                #Notificacion por email
                resultadoEnvio = self.servicio.enviar(
                    'reposicion',
                    solicitud.id, 
                    'aprobacion', 
                    destinatarios_ids, 
                    request.headers.get('Origin', '')
                )

        elif voto == 'RECHAZADO':
            # crear_mensaje_solicitud_rechazada(solicitud, request.user, comentarios)
            # encolar_validacion_rechazada_sf(
            #     solicitud=solicitud,
            #     validador=request.user,
            #     motivo=comentarios
            # )
            respmensaje = enviar_notificacion_mensajeria_interna(
                'reposicion',
                'rechazo',
                solicitud,
                destinatarios_ids,
                request.headers.get('Origin', ''),
                motivo=comentarios
            )
            #Notificacion por email
            resultadoEnvio = self.servicio.enviar(
                'reposicion',
                solicitud.id, 
                'rechazo', 
                destinatarios_ids, 
                request.headers.get('Origin', '')
            )
        
        return Response(
            ValidacionSolicitudReembolsoSerializer(validacion).data,
            status=status.HTTP_200_OK
        )


# ===================================================================
# RESETEAR VALIDACIONES
# ===================================================================
class ResetearValidacionesSolicitudReembolsoViewSet(viewsets.ViewSet):
    """
    POST /api/solicitud-reembolso/{solicitud_id}/resetear-validaciones/
    Payload: {"nueva_version": "2"}
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        self.servicio = NotificacionService()

    @transaction.atomic
    def create(self, request, solicitud_id=None):
        serializer = ResetearValidacionesSolicitudReembolsoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        solicitud = get_object_or_404(SolicitudReembolso, id=solicitud_id)
        validaciones = ValidacionSolicitudReembolso.objects.filter(solicitud=solicitud)
        nueva_version = serializer.validated_data.get('nueva_version', '2')
        reseteadas = 0
        destinatarios_ids = list(validaciones.values_list('usuarioValidador_id', flat=True))

        for v in validaciones:
            v.estado = 'PENDIENTE'
            v.versionDocumento = nueva_version
            v.fechaResolucion = None
            v.comentarios = ''
            v.save()
            reseteadas += 1

        
        respmensaje = enviar_notificacion_mensajeria_interna(
                'viaje',
                'nueva_revision',
                solicitud,
                destinatarios_ids,
                request.headers.get('Origin', ''),
                version=nueva_version,
            )
        
        #Notificacion por email
        resultadoEnvio = self.servicio.enviar(
                'viaje',
                solicitud.id, 
                'nueva_revision', 
                destinatarios_ids, 
                request.headers.get('Origin', '')
            )
        
        # for v in validaciones:
        #     encolar_revision_solicitud_fondos(
        #         solicitud=solicitud,
        #         validador=v.usuarioValidador,
        #         version=nueva_version,
        #         enlace_ver_detalle=f"/solicitudes-reembolso/{solicitud.id}/validar"
        #     )
        #     crear_mensaje_revision_solicitud_fondos(
        #         solicitud=solicitud,
        #         validador={
        #             'id': v.usuarioValidador.id,
        #             'nombre_completo': v.usuarioValidador.get_full_name(),
        #             'rol': v.usuarioValidador.cargo or 'validador',
        #             'estado': 'PENDIENTE',
        #             'fechaAsignacion': str(timezone.now())
        #         },
        #         version=nueva_version
        #     )
        
        return Response({
            'mensaje': f'Reseteadas {reseteadas} validaciones a versión {nueva_version}',
            'documento_id': solicitud.id,
            'documento_numero': solicitud.numeroFormulario or f"SR-{solicitud.id}",
            'nueva_version': nueva_version
        }, status=status.HTTP_200_OK)


# ===================================================================
# ESTADO DE VALIDACIÓN
# ===================================================================
class EstadoValidacionSolicitudReembolsoAPIView(APIView):
    """
    GET /api/solicitud-reembolso/{solicitud_id}/estado-validacion/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, solicitud_id):
        solicitud = get_object_or_404(SolicitudReembolso, id=solicitud_id)
        estadisticas = repo.obtener_estadisticas_por_solicitud(solicitud_id)

        if solicitud.actividad_id and not solicitud.tarea_id:
            tipo = 'ACTIVIDAD'
        elif solicitud.actividad_id and solicitud.tarea_id:
            tipo = 'TAREA'
        else:
            tipo = 'GENERAL'

        return Response({
            'solicitud_id': solicitud.id,
            'solicitud_codigo': solicitud.numeroFormulario or f"SR-{solicitud.id}",
            'monto': str(solicitud.montoSolicitado) if solicitud.montoSolicitado else '0.00',
            'tipo_solicitud': tipo,
            **estadisticas
        }, status=status.HTTP_200_OK)


# ===================================================================
# HISTORIAL
# ===================================================================
class HistorialValidacionSolicitudReembolsoAPIView(APIView):
    """
    GET /api/solicitud-reembolso/{solicitud_id}/historial/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, solicitud_id):
        solicitud = get_object_or_404(SolicitudReembolso, id=solicitud_id)

        from ..models import HistorialValidacion
        historial = HistorialValidacion.objects.filter(
            validacion__validacionsolicitudreembolso__solicitud=solicitud
        ).select_related('usuario', 'validacion__validacionsolicitudreembolso').order_by('-fechaCambio')

        serializer = HistorialValidacionSerializer(historial, many=True)

        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        }, status=status.HTTP_200_OK)


# ===================================================================
# MIS VALIDACIONES PENDIENTES
# ===================================================================
class MisValidacionesPendientesSolicitudReembolsoAPIView(APIView):
    """
    GET /api/solicitud-reembolso/mis-pendientes/
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
                'solicitud_codigo': v.solicitud.numeroFormulario or f"SR-{v.solicitud.id}",
                'solicitud_monto': str(v.solicitud.montoSolicitado) if v.solicitud.montoSolicitado else '0.00',
                'solicitante_nombre': v.usuarioRedactor.get_full_name() if v.usuarioRedactor else 'N/A',
                'tipo_solicitud': v.tipo_solicitud,
            })
        
        return Response({
            'count': len(data),
            'results': data
        }, status=status.HTTP_200_OK)


# ===================================================================
# ASIGNAR VALIDADORES SIN NOTIFICACIONES
# ===================================================================
class AsignarValidadoresSolicitudReembolsoSinNotificacionViewSet(viewsets.ViewSet):
    """
    POST /api/solicitud-reembolso/{solicitud_id}/asignar-validadores-sin-notificacion/
    """
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def create(self, request, solicitud_id=None):
        serializer = AsignarValidadoresSolicitudReembolsoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        solicitud = get_object_or_404(SolicitudReembolso, id=solicitud_id)
        validadores = Usuario.objects.filter(id__in=data['validador_ids'])
        
        if len(validadores) != len(data['validador_ids']):
            ids_encontrados = list(validadores.values_list('id', flat=True))
            ids_faltantes = set(data['validador_ids']) - set(ids_encontrados)
            return Response(
                {'error': f'Validadores no encontrados: {list(ids_faltantes)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        duplicados = []
        for validador in validadores:
            if repo.existe_validador(solicitud.id, 'solicitud', validador.id):
                duplicados.append({
                    'validador_id': validador.id,
                    'nombre': validador.get_full_name(),
                    'error': 'Ya existe una validación para este usuario en esta solicitud'
                })
        
        if duplicados:
            return Response({
                'error': 'Validadores duplicados encontrados',
                'detalle': duplicados
            }, status=status.HTTP_409_CONFLICT)
        
        resultados = []
        for validador in validadores:
            validacion = repo.crear(
                solicitud=solicitud,
                usuarioValidador=validador,
                usuarioRedactor=request.user,
                estado='PENDIENTE',
                versionDocumento='1'
            )
            resultados.append(
                ValidacionSolicitudReembolsoSerializer(validacion).data
            )
        
        return Response({
            'mensaje': f'Creadas {len(resultados)} validaciones (sin notificación)',
            'resultados': resultados
        }, status=status.HTTP_201_CREATED)