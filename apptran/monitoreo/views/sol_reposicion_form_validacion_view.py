# spme/apptran/monitoreo/views/sol_reposicion_form_validacion_view.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from spme_monitoreo.models import SolicitudReembolso

from ..serializers.sol_reposicion_form_validacion_serializer import (
    SolicitudReembolsoSerializer,
)


class SolicitudReembolsoFormValidacionViewSet(viewsets.ModelViewSet):
    queryset = SolicitudReembolso.objects.all()
    serializer_class = SolicitudReembolsoSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        select_related con las FK reales del modelo:
        formaPago, responsable, coordinador, usuario, actividad, tarea
        """
        queryset = SolicitudReembolso.objects.select_related(
            'formaPago',
            'responsable',
            'coordinador',
            'usuario',
            'actividad',
            'tarea',
        )

        # Filtros opcionales por query params
        usuario_id = self.request.query_params.get('usuario_id')
        if usuario_id:
            queryset = queryset.filter(usuario_id=usuario_id)

        actividad_id = self.request.query_params.get('actividad_id')
        if actividad_id:
            queryset = queryset.filter(actividad_id=actividad_id)

        validacion = self.request.query_params.get('validacion')
        if validacion:
            if validacion.lower() == 'responsable':
                queryset = queryset.filter(validacionResponsable=True)
            elif validacion.lower() == 'coordinador':
                queryset = queryset.filter(validacionCoordinador=True)
            elif validacion.lower() == 'pendiente':
                queryset = queryset.filter(
                    validacionResponsable=False,
                    validacionCoordinador=False
                )

        return queryset

    @action(detail=True, methods=['get'])
    def detalle_completo(self, request, pk=None):
        """
        Endpoint que devuelve una solicitud con toda la info anidada
        (forma_pago_info, responsable_info, coordinador_info, usuario_info,
        actividad_info, tarea_info).
        """
        solicitud = self.get_object()
        serializer = SolicitudReembolsoSerializer(
            solicitud, context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def mis_solicitudes(self, request):
        """Solicitudes del usuario autenticado"""
        queryset = self.get_queryset().filter(usuario=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_validar(self, request):
        """Solicitudes pendientes de validación (responsable y coordinador)"""
        queryset = self.get_queryset().filter(
            validacionResponsable=False,
            validacionCoordinador=False
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)