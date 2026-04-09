# spme_monitoreo/views/vinculacion_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from spme_monitoreo.modelos_vinculaciones import VinculacionSolicitudInforme
from spme_monitoreo.models import (
    SolicitudViaje, 
    InformeActividadPrincipal
    )

from ..serializers.vincular_solicitudes_viaje_a_informe_actividad_serializer import (
    SolicitudViajeVinculadaSerializer,
    VinculacionSolicitudInformeSerializer,
    VincularSolicitudSerializer,
    DesvincularSolicitudSerializer
)


class VinculacionInformeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar vinculaciones de solicitudes de viaje a informes.
    
    Endpoints:
    - GET /api/vinculaciones/ - Listar vinculaciones
    - GET /api/vinculaciones/{id}/ - Detalle
    - POST /api/vinculaciones/ - Crear vinculación
    - DELETE /api/vinculaciones/{id}/ - Eliminar vinculación
    - POST /api/vinculaciones/vincular/ - Vincular solicitud a informe
    - POST /api/vinculaciones/desvincular/ - Desvincular
    - GET /api/vinculaciones/solicitudes-disponibles/ - Solicitudes disponibles
    - POST /api/vinculaciones/{id}/reactivar/ - Reactivar vinculación
    - GET /api/vinculaciones/{id}/historial/ - Historial de la solicitud
    - GET /api/vinculaciones/por-informe/{id}/ - Vinculaciones de un informe
    """
    
    queryset = VinculacionSolicitudInforme.objects.all()
    serializer_class = VinculacionSolicitudInformeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar queryset según parámetros de consulta"""
        queryset = super().get_queryset()
        
        # Filtro por informe
        informe_id = self.request.query_params.get('informe_id')
        if informe_id:
            queryset = queryset.filter(informe_id=informe_id)
        
        # Filtro por solicitud
        solicitud_id = self.request.query_params.get('solicitud_id')
        if solicitud_id:
            queryset = queryset.filter(solicitud_id=solicitud_id)
        
        # Filtro por estado activo
        activa = self.request.query_params.get('activa')
        if activa is not None:
            queryset = queryset.filter(activa=activa.lower() == 'true')
        
        # Filtro por usuario
        usuario_id = self.request.query_params.get('usuario_id')
        if usuario_id:
            queryset = queryset.filter(usuario_vinculo_id=usuario_id)
        
        # ========== NUEVOS FILTROS ==========
        # Filtro por actividad de la solicitud
        actividad_id = self.request.query_params.get('actividad_id')
        if actividad_id:
            queryset = queryset.filter(solicitud__actividad_id=actividad_id)
        
        # Filtro por tarea de la solicitud
        tarea_id = self.request.query_params.get('tarea_id')
        if tarea_id:
            queryset = queryset.filter(solicitud__tarea_id=tarea_id)
        
        # Filtro por presencia de tarea
        tiene_tarea = self.request.query_params.get('tiene_tarea')
        if tiene_tarea is not None:
            if tiene_tarea.lower() == 'true':
                queryset = queryset.filter(solicitud__tarea__isnull=False)
            elif tiene_tarea.lower() == 'false':
                queryset = queryset.filter(solicitud__tarea__isnull=True)
        # ===================================
        
        # Optimizar consultas con select_related
        queryset = queryset.select_related(
            'solicitud', 
            'informe', 
            'usuario_vinculo',
            'solicitud__actividad',  # Para acceso eficiente a actividad
            'solicitud__tarea'       # Para acceso eficiente a tarea
        )
        
        return queryset
    
    def perform_create(self, serializer):
        """Al crear, asignar automáticamente el usuario actual"""
        serializer.save(usuario_vinculo=self.request.user)
    
    @action(detail=False, methods=['get'], url_path='solicitudes-disponibles')
    def solicitudes_disponibles(self, request):
        """
        Obtener solicitudes de viaje disponibles para vincular.
        
        Query params:
        - buscar: Texto para búsqueda
        - informe_id: ID del informe (filtra por actividad del informe)
        - actividad_id: ID de la actividad (filtra directamente por actividad)
        - tipo_solicitud: Filtra por tipo de relación
            * 'solo_actividad' - Solicitudes con actividad Y tarea = null
            * 'con_tarea' - Solicitudes con actividad Y tarea (no null)
        """
        buscar = request.query_params.get('buscar', '')
        informe_id = request.query_params.get('informe_id')
        actividad_id = request.query_params.get('actividad_id')
        tarea_id = request.query_params.get('tarea_id') 
        tipo_solicitud = request.query_params.get('tipo_solicitud', '')

        # Solicitudes con vinculación activa (excluir)
        solicitudes_vinculadas = VinculacionSolicitudInforme.objects.filter(
            activa=True
        ).values_list('solicitud_id', flat=True)
        
        # Base: solicitudes de viaje aprobadas y no vinculadas activamente
        solicitudes = SolicitudViaje.objects.filter(
            validacionCoordinador=True,  # Regla R3: Aprobaciones
            validacionResponsable=True
        ).exclude(
            id__in=solicitudes_vinculadas  # Regla R1: Sin vinculación activa
        )

        #Filtro: por tipo de ralacion (actividad/tarea)
        if(tipo_solicitud) == 'solo_actividad':
            #Solicitudes con actividad No NUll y tarea = null
            solicitudes = solicitudes.filter(
                actividad__isnull=False,
                tarea__isnull=True
            )
        elif tipo_solicitud == 'con_tarea':
            #Solicitudes con actividad NO NULL y tarea NO NULL
            solicitudes = solicitudes.filter(
                actividad__isnull=False,
                tarea__isnull=False
            )
        
        #Filtro: por actividad especifica
        if actividad_id:
            solicitudes = solicitudes.filter(actividad_id=actividad_id)

        #Filtro: por tarea especifica
        if tarea_id:
            solicitudes = solicitudes.filter(tarea_id=tarea_id)

        # Filtrar por actividad del informe (alternativa)
        if informe_id:
            informe = get_object_or_404(InformeActividadPrincipal, id=informe_id)
            if informe.actividad:
                solicitudes = solicitudes.filter(actividad=informe.actividad)
        
        # Búsqueda por texto
        if buscar:
            solicitudes = solicitudes.filter(
                Q(numeroFormulario__icontains=buscar) |
                Q(evento__icontains=buscar) |
                Q(lugarEvento__icontains=buscar)
            )

        #Ordenar
        solicitudes = solicitudes.order_by('-fechaSolicitud')

        # Paginación
        page = self.paginate_queryset(solicitudes)
        if page is not None:
            serializer = SolicitudViajeVinculadaSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        #Validacion de los datos
        serializer = SolicitudViajeVinculadaSerializer(solicitudes, many=True)

        return Response({
            'total': solicitudes.count(),
            'solicitudes': serializer.data
        })
    
    @action(detail=False, methods=['post'], url_path='vincular')
    def vincular(self, request):
        """
        Vincular una solicitud de viaje a un informe de actividad.
        
        Body:
        {
            "solicitud_id": 123,
            "informe_id": 456,
            "observaciones": "Texto opcional"
        }
        """
        # Validar datos de entrada
        validator = VincularSolicitudSerializer(data=request.data)
        validator.is_valid(raise_exception=True)
        
        solicitud_id = validator.validated_data['solicitud_id']
        informe_id = validator.validated_data['informe_id']
        observaciones = validator.validated_data.get('observaciones', '')
        
        # Obtener objetos
        solicitud = get_object_or_404(SolicitudViaje, id=solicitud_id)
        informe = get_object_or_404(InformeActividadPrincipal, id=informe_id)
        
        # Crear vinculación
        try:
            vinculacion = VinculacionSolicitudInforme.objects.create(
                solicitud=solicitud,
                informe=informe,
                usuario_vinculo=request.user,  # ← Asigna el usuario autenticado
                observaciones=observaciones,
                activa=True
            )
        except ValidationError as e:
            return Response(
                {'error': dict(e) if hasattr(e, 'error_dict') else str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Respuesta
        serializer = VinculacionSolicitudInformeSerializer(vinculacion)
        return Response({
            'message': f'Solicitud {solicitud.numeroFormulario} vinculada exitosamente al informe {informe.numeroInforme}',
            'vinculacion': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'], url_path='desvincular')
    def desvincular(self, request):
        """
        Desvincular una solicitud de viaje de un informe.
        
        Body:
        {
            "solicitud_id": 123,
            "informe_id": 456
        }
        """
        validator = DesvincularSolicitudSerializer(data=request.data)
        validator.is_valid(raise_exception=True)
        
        vinculacion = validator.validated_data['vinculacion']
        solicitud = vinculacion.solicitud
        informe = vinculacion.informe
        
        # Desactivar la vinculación
        vinculacion.desactivar()
        
        return Response({
            'message': f'Solicitud {solicitud.numeroFormulario} desvinculada del informe {informe.numeroInforme}',
            'solicitud_id': solicitud.id,
            'informe_id': informe.id,
            'vinculacion_desactivada': vinculacion.id
        })
    
    @action(detail=True, methods=['post'], url_path='reactivar')
    def reactivar(self, request, pk=None):
        """
        Reactivar una vinculación previamente desactivada.
        
        POST: /api/vinculaciones/{id}/reactivar/
        """
        vinculacion = self.get_object()
        
        if vinculacion.activa:
            return Response(
                {'error': 'La vinculación ya está activa.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            vinculacion.reactivar()
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(vinculacion)
        return Response({
            'message': 'Vinculación reactivada exitosamente.',
            'vinculacion': serializer.data
        })
    
    @action(detail=True, methods=['get'], url_path='historial')
    def historial(self, request, pk=None):
        """
        Obtener historial completo de vinculaciones de una solicitud.
        
        GET: /api/vinculaciones/{solicitud_id}/historial/
        """
        vinculacion = self.get_object()
        solicitud = vinculacion.solicitud
        
        historial = VinculacionSolicitudInforme.objects.filter(
            solicitud=solicitud
        ).order_by('-fecha_vinculacion')
        
        serializer = VinculacionSolicitudInformeSerializer(historial, many=True)
        
        return Response({
            'solicitud_id': solicitud.id,
            'solicitud_numero': solicitud.numeroFormulario,
            'solicitud_evento': solicitud.evento,
            'total_vinculaciones': historial.count(),
            'tiene_vinculacion_activa': historial.filter(activa=True).exists(),
            'historial': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='por-informe/(?P<informe_id>[^/.]+)')
    def por_informe(self, request, informe_id=None):
        """
        Obtener todas las vinculaciones de un informe específico.
        
        GET: /api/vinculaciones/por-informe/{informe_id}/
        """
        informe = get_object_or_404(InformeActividadPrincipal, id=informe_id)
        
        vinculaciones = self.get_queryset().filter(
            informe=informe,
            activa=True
        )
        
        serializer = self.get_serializer(vinculaciones, many=True)
        
        monto_total = sum(
            v.solicitud.montoSolicitado or 0 for v in vinculaciones
        )
        
        return Response({
            'informe_id': informe.id,
            'informe_numero': informe.numeroInforme,
            'total_solicitudes': vinculaciones.count(),
            'monto_total': monto_total,
            'solicitudes': serializer.data
        })