from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

# Models
from spme_monitoreo.models import RendicionCuentas
from spme_autenticacion.models import Usuario
from ..models import ValidacionRendicionCuentas

# Serializers
from ..serializers.validaciones_rendicion_cuentas_serializers import (
    ValidacionRendicionCuentasSerializer,
    AsignarValidadoresRendicionCuentasSerializer,
    ResetearValidacionesRendicionCuentasSerializer,
)

# Services
from ..services.validacion_rendicion_cuentas_service import ValidacionRendicionCuentasService

# Repositories
from ..repositories.validacion_rendicion_cuentas_repository import ValidacionRendicionCuentasRepository

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

import logging

logger = logging.getLogger(__name__)
repo = ValidacionRendicionCuentasRepository()


# ===================================================================
# ASIGNAR VALIDADORES
# ===================================================================
class AsignarValidadoresRendicionCuentasViewSet(viewsets.ViewSet):
    """
    POST /api/rendicion-cuentas/{id}/asignar-validadores/ 
    - Payload: {"validador_ids": [2,3]}
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create(self, request, rendicion_id=None):
        serializer = AsignarValidadoresRendicionCuentasSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        rendicion = get_object_or_404(RendicionCuentas, id=rendicion_id)
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
                if repo.existe_validador(rendicion.id, 'rendicion', validador.id):
                    errores.append({
                        'validador_id': validador.id,
                        'error': f'Ya existe validación para {validador.get_full_name()}'
                    })
                    continue
                
                v = repo.crear(
                    rendicion=rendicion,
                    usuarioValidador=validador,
                    usuarioRedactor=request.user,
                    estado='PENDIENTE',
                    versionDocumento='1'
                )
                resultados.append(ValidacionRendicionCuentasSerializer(v).data)
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
        
        #Notificacion y mensaje
        # if validadores_json:
        #     crear_mensajes_validacion_solicitud_fondos(rendicion, validadores_json)
        #     for val in validadores:
        #         encolar_validacion_pendiente_sf(
        #             solicitud=rendicion,
        #             validador=val,
        #             enlace_ver_detalle=f"/rendiciones-cuentas/{rendicion.id}/validar"
        #         )
        return Response({
            'mensaje': f'Creadas {len(resultados)} validaciones',
            'errores': errores if errores else None,
            'resultados': resultados
        }, status=status.HTTP_201_CREATED)


# ===================================================================
# EMITIR VOTO
# ===================================================================
class VotarRendicionCuentasViewSet(viewsets.ViewSet):
    """
    POST /api/rendicion-cuentas/{rendicion_id}/votar/
    Payload: {"validacion_id": 15, "estado": "APROBADO", "comentarios": "..."}
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create(self, request, rendicion_id=None):
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
            validacion = ValidacionRendicionCuentas.objects.get(
                id=validacion_id,
                usuarioValidador=request.user,
                estado='PENDIENTE'
            )
        except ValidacionRendicionCuentas.DoesNotExist:
            return Response(
                {'error': 'Validación no encontrada o ya procesada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        validacion.estado = voto
        validacion.comentarios = comentarios
        validacion.save()
        
        rendicion = validacion.rendicion

        # encolar_confirmacion_validador_sf(
        #     solicitud=rendicion,
        #     validador=request.user,
        #     accion=voto.lower()
        # )

        if voto == 'APROBADO':
            resumen = repo.obtener_resumen_estado_rendicion(rendicion.id)
            if resumen['aprobado_totalmente']:
                validaciones_aprobadas = ValidacionRendicionCuentas.objects.filter(
                    rendicion=rendicion, estado='APROBADO'
                )
                crear_mensaje_solicitud_aprobada(rendicion, validaciones_aprobadas)
                # encolar_validacion_aprobada_sf(
                #     solicitud=rendicion,
                #     validador=request.user
                # )

        elif voto == 'RECHAZADO':
            crear_mensaje_solicitud_rechazada(rendicion, request.user, comentarios)
            # encolar_validacion_rechazada_sf(
            #     solicitud=rendicion,
            #     validador=request.user,
            #     motivo=comentarios
            # )
        
        return Response(
            ValidacionRendicionCuentasSerializer(validacion).data,
            status=status.HTTP_200_OK
        )


# ===================================================================
# RESETEAR VALIDACIONES
# ===================================================================
class ResetearValidacionesRendicionCuentasViewSet(viewsets.ViewSet):
    """
    POST /api/rendicion-cuentas/{rendicion_id}/resetear-validaciones/
    Payload: {"nueva_version": "2"}
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create(self, request, rendicion_id=None):
        serializer = ResetearValidacionesRendicionCuentasSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        rendicion = get_object_or_404(RendicionCuentas, id=rendicion_id)
        validaciones = ValidacionRendicionCuentas.objects.filter(rendicion=rendicion)
        nueva_version = serializer.validated_data.get('nueva_version', '2')
        reseteadas = 0

        for v in validaciones:
            v.estado = 'PENDIENTE'
            v.versionDocumento = nueva_version
            v.fechaResolucion = None
            v.save()
            reseteadas += 1
        
        for v in validaciones:
            # encolar_revision_solicitud_fondos(
            #     solicitud=rendicion,
            #     validador=v.usuarioValidador,
            #     version=nueva_version,
            #     enlace_ver_detalle=f"/rendiciones-cuentas/{rendicion.id}/validar"
            # )
            crear_mensaje_revision_solicitud_fondos(
                solicitud=rendicion,
                validador={
                    'id': v.usuarioValidador.id,
                    'nombre_completo': v.usuarioValidador.get_full_name(),
                    'rol': v.usuarioValidador.cargo or 'validador',
                    'estado': 'PENDIENTE',
                    'fechaAsignacion': str(timezone.now())
                },
                version=nueva_version
            )
        
        return Response({
            'mensaje': f'Reseteadas {reseteadas} validaciones a versión {nueva_version}',
            'documento_id': rendicion.id,
            'documento_numero': rendicion.numeroFormulario or f"RC-{rendicion.id}",
            'nueva_version': nueva_version
        }, status=status.HTTP_200_OK)


# ===================================================================
# ESTADO DE VALIDACIÓN
# ===================================================================
class EstadoValidacionRendicionCuentasAPIView(APIView):
    """
    GET /api/rendicion-cuentas/{rendicion_id}/estado-validacion/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, rendicion_id):
        rendicion = get_object_or_404(RendicionCuentas, id=rendicion_id)
        estadisticas = repo.obtener_estadisticas_por_rendicion(rendicion_id)

        if rendicion.actividad_id and not rendicion.tarea_id:
            tipo = 'ACTIVIDAD'
        elif rendicion.actividad_id and rendicion.tarea_id:
            tipo = 'TAREA'
        else:
            tipo = 'GENERAL'

        return Response({
            'rendicion_id': rendicion.id,
            'rendicion_codigo': rendicion.numeroFormulario or f"RC-{rendicion.id}",
            'monto_asignado': str(rendicion.montoAsignado) if rendicion.montoAsignado else '0.00',
            'monto_descargado': str(rendicion.montoDescargado) if rendicion.montoDescargado else '0.00',
            'saldo': str(rendicion.saldo) if rendicion.saldo else '0.00',
            'tipo_rendicion': tipo,
            **estadisticas
        }, status=status.HTTP_200_OK)


# ===================================================================
# HISTORIAL
# ===================================================================
class HistorialValidacionRendicionCuentasAPIView(APIView):
    """
    GET /api/rendicion-cuentas/{rendicion_id}/historial/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, rendicion_id):
        rendicion = get_object_or_404(RendicionCuentas, id=rendicion_id)

        from ..models import HistorialValidacion
        historial = HistorialValidacion.objects.filter(
            validacion__validacionrendicioncuentas__rendicion=rendicion
        ).select_related('usuario', 'validacion__validacionrendicioncuentas').order_by('-fechaCambio')

        serializer = HistorialValidacionSerializer(historial, many=True)

        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        }, status=status.HTTP_200_OK)


# ===================================================================
# MIS VALIDACIONES PENDIENTES
# ===================================================================
class MisValidacionesPendientesRendicionCuentasAPIView(APIView):
    """
    GET /api/rendicion-cuentas/mis-pendientes/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        validaciones = repo.obtener_por_validador_con_rendicion(request.user.id)
        pendientes = [v for v in validaciones if v.estado == 'PENDIENTE']

        data = []
        for v in pendientes:
            data.append({
                'validacion_id': v.id,
                'codigo_seguimiento': v.codigoSeguimiento,
                'estado': v.estado,
                'fecha_asignacion': v.fechaAsignacion,
                'rendicion_id': v.rendicion.id,
                'rendicion_codigo': v.rendicion.numeroFormulario or f"RC-{v.rendicion.id}",
                'monto_asignado': str(v.rendicion.montoAsignado) if v.rendicion.montoAsignado else '0.00',
                'monto_descargado': str(v.rendicion.montoDescargado) if v.rendicion.montoDescargado else '0.00',
                'saldo': str(v.rendicion.saldo) if v.rendicion.saldo else '0.00',
                'solicitante_nombre': v.usuarioRedactor.get_full_name() if v.usuarioRedactor else 'N/A',
                'tipo_rendicion': v.tipo_rendicion,
            })
        
        return Response({
            'count': len(data),
            'results': data
        }, status=status.HTTP_200_OK)


# ===================================================================
# ASIGNAR VALIDADORES SIN NOTIFICACIONES
# ===================================================================
class AsignarValidadoresRendicionCuentasSinNotificacionViewSet(viewsets.ViewSet):
    """
    POST /api/rendicion-cuentas/{rendicion_id}/asignar-validadores-sin-notificacion/
    """
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def create(self, request, rendicion_id=None):
        serializer = AsignarValidadoresRendicionCuentasSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        rendicion = get_object_or_404(RendicionCuentas, id=rendicion_id)
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
            if repo.existe_validador(rendicion.id, 'rendicion', validador.id):
                duplicados.append({
                    'validador_id': validador.id,
                    'nombre': validador.get_full_name(),
                    'error': 'Ya existe una validación para este usuario en esta rendición'
                })
        
        if duplicados:
            return Response({
                'error': 'Validadores duplicados encontrados',
                'detalle': duplicados
            }, status=status.HTTP_409_CONFLICT)
        
        resultados = []
        for validador in validadores:
            validacion = repo.crear(
                rendicion=rendicion,
                usuarioValidador=validador,
                usuarioRedactor=request.user,
                estado='PENDIENTE',
                versionDocumento='1'
            )
            resultados.append(
                ValidacionRendicionCuentasSerializer(validacion).data
            )
        
        return Response({
            'mensaje': f'Creadas {len(resultados)} validaciones (sin notificación)',
            'resultados': resultados
        }, status=status.HTTP_201_CREATED)