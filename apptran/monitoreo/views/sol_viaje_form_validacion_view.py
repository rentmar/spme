# spme/apptran/monitoreo/views/sol_viaje_form_validacion_view.py
# views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from spme_monitoreo.models import SolicitudViaje
from ..serializers.sol_viaje_form_validacion_serializer import (
    SolicitudViajeSerializer,
    # Si tienes serializers específicos, agrégalos aquí:
    # SolicitudViajeCreateSerializer,
    # SolicitudViajeUpdateSerializer,
    # SolicitudViajeValidationSerializer,
)


class SolicitudViajeFormValidarViewSet(viewsets.ModelViewSet):
    queryset = SolicitudViaje.objects.all()
    serializer_class = SolicitudViajeSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Optimiza las consultas con select_related para evitar el problema N+1,
        ya que el serializer accede a muchas FK (formaPago, responsable,
        coordinador, usuario, actividad, tarea).
        """
        queryset = SolicitudViaje.objects.select_related(
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

    def get_serializer_class(self):
        # Si más adelante creas serializers específicos, selecciónalos aquí
        # if self.action == 'create':
        #     return SolicitudViajeCreateSerializer
        # elif self.action in ['update', 'partial_update']:
        #     return SolicitudViajeUpdateSerializer
        return SolicitudViajeSerializer

    @action(detail=True, methods=['get'])
    def detalle_completo(self, request, pk=None):
        """
        Endpoint que devuelve una solicitud con toda la info anidada
        (forma_pago_info, coordinador_info, usuario_info, actividad_info, tarea_info).
        """
        solicitud = self.get_object()
        serializer = SolicitudViajeSerializer(solicitud, context={'request': request})
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