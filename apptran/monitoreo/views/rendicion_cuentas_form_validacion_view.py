# spme/apptran/monitoreo/views/rendicion_cuentas_form_validacion_view.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from spme_monitoreo.models import RendicionCuentas

from ..serializers.rendicion_cuentas_form_validacion_serializer import (
    RendicionCuentasSerializer,
)


class RendicionCuentasFormValidacionViewSet(viewsets.ModelViewSet):
    queryset = RendicionCuentas.objects.all()
    serializer_class = RendicionCuentasSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        select_related con las FK reales del modelo:
        actividad, tarea, responsable, coordinador, contador, administrador, usuario,
        solicitudFondos, solicitudReembolso, solicitudViaje, solicitudPagoDirecto
        """
        queryset = RendicionCuentas.objects.select_related(
            'actividad',
            'tarea',
            'responsable',
            'coordinador',
            'contador',
            'administrador',
            'usuario',
            'solicitudFondos',
            'solicitudReembolso',
            'solicitudViaje',
            'solicitudPagoDirecto',
        )

        # Filtros opcionales por query params
        usuario_id = self.request.query_params.get('usuario_id')
        if usuario_id:
            queryset = queryset.filter(usuario_id=usuario_id)

        actividad_id = self.request.query_params.get('actividad_id')
        if actividad_id:
            queryset = queryset.filter(actividad_id=actividad_id)

        tarea_id = self.request.query_params.get('tarea_id')
        if tarea_id:
            queryset = queryset.filter(tarea_id=tarea_id)

        validacion = self.request.query_params.get('validacion')
        if validacion:
            if validacion.lower() == 'responsable':
                queryset = queryset.filter(validacionResponsable=True)
            elif validacion.lower() == 'coordinador':
                queryset = queryset.filter(validacionCoordinador=True)
            elif validacion.lower() == 'contador':
                queryset = queryset.filter(validacionContador=True)
            elif validacion.lower() == 'administrador':
                queryset = queryset.filter(validacionAdministrador=True)
            elif validacion.lower() == 'pendiente':
                queryset = queryset.filter(
                    validacionResponsable=False,
                    validacionCoordinador=False
                )

        return queryset

    @action(detail=True, methods=['get'])
    def detalle_completo(self, request, pk=None):
        """
        Endpoint que devuelve una rendición con toda la info anidada
        (responsable_info, contador_info, coordinador_info, administrador_info,
        usuario_info, actividad_info, tarea_info).
        """
        rendicion = self.get_object()
        serializer = RendicionCuentasSerializer(
            rendicion, context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def mis_solicitudes(self, request):
        """Rendiciones del usuario autenticado"""
        queryset = self.get_queryset().filter(usuario=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_validar(self, request):
        """Rendiciones pendientes de validación (responsable y coordinador)"""
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