from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from spme_monitoreo.models import RendicionCuentasActPei
from ..serializers.rendicion_cuentas_pei_crud_serializer import (
    RendicionCuentasActPeiSerializer,
    RendicionCuentasActPeiObtenerPorIdSerializer,
    RendicionCuentasActPeiFiltrarSerializer,
    RendicionCuentasActPeiActualizarEstadoSerializer
)


class RendicionCuentasActPeiView(viewsets.ModelViewSet):
    queryset = RendicionCuentasActPei.objects.all()
    serializer_class = RendicionCuentasActPeiSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # Endpoint: Filtrar solicitudes por actividad_id, usuario_id, tarea_id
    @action(detail=False, methods=['post'])
    def filtrar(self, request):
        serializer = RendicionCuentasActPeiFiltrarSerializer(data=request.data)
        
        if serializer.is_valid():
            filters = {}
            actividad_id = serializer.validated_data.get('actividad_id')
            usuario_id = serializer.validated_data.get('usuario_id')
            tarea_id = serializer.validated_data.get('tarea_id')
            
            if actividad_id is not None:
                filters['actividad_id'] = actividad_id
            if usuario_id is not None:
                filters['usuario_id'] = usuario_id
            if tarea_id is not None:
                filters['tarea_id'] = tarea_id
            
            queryset = RendicionCuentasActPei.objects.filter(**filters)
            return Response(RendicionCuentasActPeiSerializer(queryset, many=True).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Endpoint: Actualizar estado de validación
    @action(detail=False, methods=['patch'])
    def actualizar_estado(self, request):
        id_serializer = RendicionCuentasActPeiObtenerPorIdSerializer(data=request.data)
        
        if not id_serializer.is_valid():
            return Response(id_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        solicitud_id = id_serializer.validated_data['id']
        
        try:
            solicitud = RendicionCuentasActPei.objects.get(id=solicitud_id)
            estado_serializer = RendicionCuentasActPeiActualizarEstadoSerializer(
                solicitud,
                data=request.data,
                partial=True
            )
            
            if estado_serializer.is_valid():
                estado_serializer.save()
                return Response(RendicionCuentasActPeiSerializer(solicitud).data)
            
            return Response(estado_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except RendicionCuentasActPei.DoesNotExist:
            return Response(
                {'error': 'Rendición de cuentas no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
