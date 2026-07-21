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
    crear_mensaje_revision_solicitud_fondos,
) 

#Notificaciones email - encolar
from spme_monitor_estados.utils.encolar import (
    encolar_validacion_pendiente,
    encolar_validacion_aprobada,
    encolar_validacion_rechazada,
    encolar_confirmacion_validador,
    encolar_validacion_pendiente_sf,
    encolar_validacion_aprobada_sf,
    encolar_validacion_rechazada_sf,
    encolar_confirmacion_validador_sf,
    encolar_revision_solicitud_fondos,
)

#Notificacion email - celery
from spme_email.services.notificacion_service import NotificacionService

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

    def __init__(self, **kwargs):
        self.servicio = NotificacionService()        
        

    @transaction.atomic
    def create(self, request, solicitud_id=None):
        serializer = AsignarValidadoresSolicitudFondosSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        solicitud = get_object_or_404(SolicitudFondos, id=solicitud_id)
        validadoresIds = serializer.validated_data['validador_ids'] 
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

        #Crear las entradas para los validadores, usando las ids recibidas
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
            # for val in validadores:
            #     encolar_validacion_pendiente_sf(
            #         solicitud=solicitud,
            #         validador=val,
            #         enlace_ver_detalle=f"/solicitudes-fondos/{solicitud.id}/validar"
            #     )
            resultadoEnvio = self.servicio.enviar('fondos',solicitud.id, 'revision', validadoresIds, request.headers.get('Origin', ''))
            
        return Response({
            'mensaje': f'Creadas {len(resultados)} validaciones',
            **resultadoEnvio,
            'errores': errores if errores else None,
            'resultados': resultados
        }, status=status.HTTP_201_CREATED)
        
# ===================================================================
# EMITIR VOTO (APROBAR O RECHAZAR)
# ===================================================================

class VotarSolicitudFondosViewSet(viewsets.ViewSet):
    """
    POST /api/solicitud-fondos/{solicitud_id}/votar/
    Payload: {"validacion_id": 15, "estado": "APROBADO", "comentarios": "..."}
    
    El mismo endpoint se usa para APROBAR y RECHAZAR.
    El campo "estado" determina la acción: "APROBADO" o "RECHAZADO".
    Si es RECHAZADO, "comentarios" es obligatorio.
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
            validacion = ValidacionSolicitudFondos.objects.get(
                id=validacion_id,
                usuarioValidador=request.user,
                estado='PENDIENTE'
            )
        except ValidacionSolicitudFondos.DoesNotExist:
            return Response(
                {'error': 'Validación no encontrada o ya procesada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        validacion.estado = voto
        validacion.comentarios = comentarios
        validacion.save()
        
        solicitud = validacion.solicitud
        context = solicitud.get_mensaje_contexto()
        solicitante_id = context['solicitante_id']  # 72
        destinatarios_ids = [solicitante_id]  # [72]

        # Confirmar al validador
        encolar_confirmacion_validador_sf(
            solicitud=solicitud,
            validador=request.user,
            accion=voto.lower()
        )

        if voto == 'APROBADO':
            resumen = repo.obtener_resumen_estado_solicitud(solicitud.id)
            if resumen['aprobado_totalmente']:
                validaciones_aprobadas = ValidacionSolicitudFondos.objects.filter(
                    solicitud=solicitud, estado='APROBADO'
                )
                crear_mensaje_solicitud_aprobada(solicitud, validaciones_aprobadas)
                # encolar_validacion_aprobada_sf(    # ← BIEN
                #     solicitud=solicitud,
                #     validador=request.user
                # )
                respuesta = self.servicio.enviar('fondos', solicitud.id, 'aprobacion', destinatarios_ids, request.headers.get('Origin', ''))


        elif voto == 'RECHAZADO':
            # crear_mensaje_solicitud_rechazada(solicitud, request.user, comentarios)
            # encolar_validacion_rechazada_sf( 
            #     solicitud=solicitud,
            #     validador=request.user,
            #     motivo=comentarios
            # )
            respuesta = self.servicio.enviar('fondos', solicitud_id, 'rechazo', destinatarios_ids, request.headers.get('Origin', ''))
        
        return Response(
            ValidacionSolicitudFondosSerializer(validacion).data,
            status=status.HTTP_200_OK
        )


# ===================================================================
# RESETEAR VALIDACIONES (MANUAL - NO AUTOMÁTICO)
# ===================================================================

class ResetearValidacionesSolicitudFondosViewSet(viewsets.ViewSet):
    """
    POST /api/solicitud-fondos/{solicitud_id}/resetear-validaciones/
    Payload: {"nueva_version": "2"}
    
    ⚠️ Este endpoint NO se llama automáticamente.
    El solicitante debe invocarlo manualmente después de corregir la solicitud.

    Resetea TODOS los validadores a PENDIENTE, actualiza la versión,
    y notifica por email + mensajería interna que se trata de una
    NUEVA REVISIÓN de un documento previamente rechazado.
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        self.servicio = NotificacionService()

    @transaction.atomic
    def create(self, request, solicitud_id=None):
        serializer = ResetearValidacionesSolicitudFondosSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        solicitud = get_object_or_404(SolicitudFondos, id=solicitud_id)
        validaciones = ValidacionSolicitudFondos.objects.filter(solicitud=solicitud)
        validadoresIds = list(ValidacionSolicitudFondos.objects.filter(solicitud=solicitud).values_list('usuarioValidador_id', flat=True).distinct()) 
        nueva_version = serializer.validated_data.get('nueva_version', '2')
        reseteadas = 0

        #Resetear las validaciones
        for v in validaciones:
            v.estado = 'PENDIENTE'
            v.versionDocumento = nueva_version
            v.fechaResolucion = None
            v.comentarios = ''
            v.save()
            reseteadas += 1
        
        #Notificar a cada validadores
        for v in validaciones:
            # 📧 Email: Nueva revisión de documento previamente rechazado
            # encolar_revision_solicitud_fondos(
            #     solicitud=solicitud,
            #     validador=v.usuarioValidador,
            #     version=nueva_version,
            #     enlace_ver_detalle=f"/solicitudes-fondos/{solicitud.id}/validar"
            # )
            # 🔔 Mensajería interna: Nueva revisión
            crear_mensaje_revision_solicitud_fondos(
                solicitud=solicitud,
                validador={
                    'id': v.usuarioValidador.id,
                    'nombre_completo': v.usuarioValidador.get_full_name(),
                    'rol': v.usuarioValidador.cargo or 'validador',
                    'estado': 'PENDIENTE',
                    'fechaAsignacion': str(timezone.now())
                },
                version=nueva_version
            )
        
        respuesta = self.servicio.enviar('fondos', solicitud_id, 'nueva_revision', validadoresIds, request.headers.get('Origin', ''))
        
        
        return Response({
            'mensaje': f'Reseteadas {reseteadas} validaciones a versión {nueva_version}',
            'documento_id': solicitud.id,
            'documento_numero': solicitud.numeroFormulario or f"SF-{solicitud.id}",
            'nueva_version': nueva_version
        }, status=status.HTTP_200_OK)

    
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
    

# ===================================================================
# ASIGNAR VALIDADORES SIN NOTIFICACIONES
# Solicitud de Fondos
# ===================================================================
class AsignarValidadoresSolicitudFondosSinNotificacionViewSet(viewsets.ViewSet):
    """
    POST /api/solicitud-fondos/{solicitud_id}/asignar-validadores-sin-notificacion/
    
    Asigna validadores SIN enviar notificaciones ni emails.
    Basado en el endpoint original pero sin llamadas a:
    - crear_mensajes_validacion_solicitud_fondos()
    - encolar_validacion_pendiente()
    
    Reglas:
    - Transacción atómica: todo el lote o nada
    - Unicidad estricta: si cualquier validador ya existe, se rechaza todo
    - Doble protección anti-duplicados: clean() en modelo + UniqueConstraint en BD
    """
    permission_classes = [IsAuthenticated]
    def create(self, request, solicitud_id=None):
        serializer = AsignarValidadoresSolicitudFondosSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        solicitud = get_object_or_404(SolicitudFondos, id=solicitud_id)
        validadores = Usuario.objects.filter(id__in=data['validador_ids'])
        
        # Validar que todos los IDs existen
        if len(validadores) != len(data['validador_ids']):
            ids_encontrados = list(validadores.values_list('id', flat=True))
            ids_faltantes = set(data['validador_ids']) - set(ids_encontrados)
            return Response(
                {'error': f'Validadores no encontrados: {list(ids_faltantes)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar UNICIDAD ESTRICTA: verificar que ninguno exista ya
        duplicados = []
        for validador in validadores:
            if repo.existe_validador(solicitud.id, 'solicitud', validador.id):
                duplicados.append({
                    'validador_id': validador.id,
                    'nombre': validador.get_full_name(),
                    'error': 'Ya existe una validación para este usuario en esta solicitud'
                })
        
        # Si hay duplicados, RECHAZAR TODO EL LOTE
        if duplicados:
            return Response({
                'error': 'Validadores duplicados encontrados',
                'detalle': duplicados
            }, status=status.HTTP_409_CONFLICT)
        
        # Todos son únicos, crear validaciones
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
                ValidacionSolicitudFondosSerializer(validacion).data
            )
        
        # ❌ SIN NOTIFICACIONES
        # ❌ SIN EMAILS
        
        return Response({
            'mensaje': f'Creadas {len(resultados)} validaciones (sin notificación)',
            'resultados': resultados
        }, status=status.HTTP_201_CREATED)
    
