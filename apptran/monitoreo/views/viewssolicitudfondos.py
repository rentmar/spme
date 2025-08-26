# views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from spme_monitoreo.models import SolicitudFondos
from ..serializers.serializarsolicitudfondos import (
    SolicitudFondosSerializer,
    SolicitudFondosCreateSerializer,
    SolicitudFondosUpdateSerializer,
    SolicitudFondosValidationSerializer
)

class SolicitudFondosViewSet(viewsets.ModelViewSet):
    queryset = SolicitudFondos.objects.all()
    #permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return SolicitudFondosCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return SolicitudFondosUpdateSerializer
        elif self.action == 'validar':
            return SolicitudFondosValidationSerializer
        return SolicitudFondosSerializer

    def perform_create(self, serializer):
        # Asignar el usuario actual si no se proporciona
        instance = serializer.save()
        if not instance.usuario:
            instance.usuario = self.request.user
            instance.save()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        # Filtrar por usuario si se solicita
        usuario_id = request.query_params.get('usuario_id')
        if usuario_id:
            queryset = queryset.filter(usuario_id=usuario_id)
        
        # Filtrar por actividad si se solicita
        actividad_id = request.query_params.get('actividad_id')
        if actividad_id:
            queryset = queryset.filter(actividad_id=actividad_id)
        
        # Filtrar por estado de validación
        validacion = request.query_params.get('validacion')
        if validacion:
            if validacion.lower() == 'responsable':
                queryset = queryset.filter(validacionResponsable=True)
            elif validacion.lower() == 'coordinador':
                queryset = queryset.filter(validacionCoordinador=True)
            elif validacion.lower() == 'pendiente':
                queryset = queryset.filter(validacionResponsable=False, validacionCoordinador=False)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def validar_responsable(self, request, pk=None):
        solicitud = self.get_object()
        serializer = SolicitudFondosValidationSerializer(
            solicitud, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save(responsable=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def validar_coordinador(self, request, pk=None):
        solicitud = self.get_object()
        serializer = SolicitudFondosValidationSerializer(
            solicitud, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save(coordinador=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def mis_solicitudes(self, request):
        """Endpoint para obtener las solicitudes del usuario autenticado"""
        queryset = self.get_queryset().filter(usuario=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_validar(self, request):
        """Endpoint para obtener solicitudes pendientes de validación"""
        queryset = self.get_queryset().filter(
            validacionResponsable=False,
            validacionCoordinador=False
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)