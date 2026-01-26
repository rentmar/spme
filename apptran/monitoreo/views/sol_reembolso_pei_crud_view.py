from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from spme_monitoreo.models import SolicitudReembolsoActPei
from ..serializers.sol_reembolso_pei_crud_serializer import (
    SolicitudReembolsoActPeiSerializer,
    SolicitudReembolsoActPeiObtenerPorIdSerializer,
    SolicitudReembolsoActPeiFiltrarSerializer,
    SolicitudReembolsoActPeiActualizarEstadoSerializer
)

class SolicitudReembolsoActPeiView(viewsets.ModelViewSet):
    queryset = SolicitudReembolsoActPei.objects.all()
    serializer_class = SolicitudReembolsoActPeiSerializer

    @action(detail=False, methods=['post'])
    def filtrar(self, request):
        serializer = SolicitudReembolsoActPeiFiltrarSerializer(data=request.data)
        
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
            
            queryset = SolicitudReembolsoActPei.objects.filter(**filters)
            return Response(SolicitudReembolsoActPeiSerializer(queryset, many=True).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['patch'])
    def actualizar_estado(self, request):
        id_serializer = SolicitudReembolsoActPeiObtenerPorIdSerializer(data=request.data)
        
        if not id_serializer.is_valid():
            return Response(id_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        solicitud_id = id_serializer.validated_data['id']
        
        try:
            solicitud = SolicitudReembolsoActPei.objects.get(id=solicitud_id)
            estado_serializer = SolicitudReembolsoActPeiActualizarEstadoSerializer(
                solicitud,
                data=request.data,
                partial=True
            )
            
            if estado_serializer.is_valid():
                estado_serializer.save()
                return Response(SolicitudReembolsoActPeiSerializer(solicitud).data)
            
            return Response(estado_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except SolicitudReembolsoActPei.DoesNotExist:
            return Response(
                {'error': 'Solicitud no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
