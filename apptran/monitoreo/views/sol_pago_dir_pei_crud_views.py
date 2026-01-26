from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from spme_monitoreo.models import SolicitudPagoDirectoActPei
from ..serializers.sol_pago_dir_pei_crud_serializer import (
    SolicitudPagoDirectoActPeiSerializer,
    SolicitudPagoDirectoActPeiObtenerPorIdSerializer,
    SolicitudPagoDirectoActPeiFiltrarSerializer,
    SolicitudPagoDirectoActPeiActualizarEstadoSerializer
)

class SolicitudPagoDirectoActPeiView(viewsets.ModelViewSet):
    queryset = SolicitudPagoDirectoActPei.objects.all()
    serializer_class = SolicitudPagoDirectoActPeiSerializer

    # Endpoint #3: Obtener solicitud por ID
    @action(detail=False, methods=['post'])
    def obtener_por_id(self, request):
        serializer = SolicitudPagoDirectoActPeiObtenerPorIdSerializer(data=request.data)
        
        if serializer.is_valid():
            solicitud_id = serializer.validated_data['id']
            try:
                solicitud = SolicitudPagoDirectoActPei.objects.get(id=solicitud_id)
                return Response(SolicitudPagoDirectoActPeiSerializer(solicitud).data)
            except SolicitudPagoDirectoActPei.DoesNotExist:
                return Response(
                    {'error': 'Solicitud no encontrada'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Endpoint #4: Filtrar solicitudes
    @action(detail=False, methods=['post'])
    def filtrar(self, request):
        serializer = SolicitudPagoDirectoActPeiFiltrarSerializer(data=request.data)
        
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
            
            queryset = SolicitudPagoDirectoActPei.objects.filter(**filters)
            return Response(SolicitudPagoDirectoActPeiSerializer(queryset, many=True).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Endpoint #5: Actualizar estado de validación
    @action(detail=False, methods=['patch'])
    def actualizar_estado(self, request):
        id_serializer = SolicitudPagoDirectoActPeiObtenerPorIdSerializer(data=request.data)
        
        if not id_serializer.is_valid():
            return Response(id_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        solicitud_id = id_serializer.validated_data['id']
        
        try:
            solicitud = SolicitudPagoDirectoActPei.objects.get(id=solicitud_id)
            estado_serializer = SolicitudPagoDirectoActPeiActualizarEstadoSerializer(
                solicitud,
                data=request.data,
                partial=True
            )
            
            if estado_serializer.is_valid():
                estado_serializer.save()
                return Response(SolicitudPagoDirectoActPeiSerializer(solicitud).data)
            
            return Response(estado_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except SolicitudPagoDirectoActPei.DoesNotExist:
            return Response(
                {'error': 'Solicitud no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )