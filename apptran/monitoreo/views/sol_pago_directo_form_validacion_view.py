# views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from spme_monitoreo.models import SolicitudPagoDirecto

from ..serializers.sol_pago_directo_form_serializer import (
    SolicitudPagoDirectoSerializer
)


class SolicitudPagoDirectoFormValidacionViewSet(viewsets.ModelViewSet):
    queryset = SolicitudPagoDirecto.objects.all()
    serializer_class = SolicitudPagoDirectoSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Optimiza las consultas con select_related para evitar el problema N+1.
        FK reales del modelo: formaPago, contador, coordinador, usuario, actividad, tarea
        """
        queryset = SolicitudPagoDirecto.objects.select_related(
            'formaPago',
            'contador',
            'coordinador',
            'usuario',
            'actividad',
            'tarea',
        )

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
        solicitud = self.get_object()
        serializer = SolicitudPagoDirectoSerializer(
            solicitud, context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def mis_solicitudes(self, request):
        queryset = self.get_queryset().filter(usuario=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_validar(self, request):
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