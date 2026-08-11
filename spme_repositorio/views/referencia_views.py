from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from spme_repositorio.serializers.referencia_serializers import (
    ReferenciaSerializer,
    ReferenciaSingleRequestSerializer,
    ReferenciaBulkRequestSerializer,
)
from spme_repositorio.services.referencias.referencia_service import ReferenciaService
from spme_repositorio.nodos_config import get_modelo


class ReferenciaListView(APIView):
    """GET /api-repo/referencias/{tipo_objeto}/{objeto_id}/"""

    def get(self, request, tipo_objeto, objeto_id):
        model = get_modelo(tipo_objeto)
        if model is None:
            return Response(
                {'error': f"Tipo de objeto no permitido: '{tipo_objeto}'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        obj = model.objects.filter(pk=objeto_id).first()
        if obj is None:
            return Response(
                {'error': f"Objeto no encontrado: {tipo_objeto}#{objeto_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        service = ReferenciaService()
        refs = service.obtener_referencias(obj)
        return Response(ReferenciaSerializer(refs, many=True).data)


class ReferenciaSingleView(APIView):
    """POST /api-repo/referencias/"""

    def post(self, request):
        serializer = ReferenciaSingleRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        model = get_modelo(data['tipo_objeto'])
        if model is None:
            return Response(
                {'error': f"Tipo de objeto no permitido: '{data['tipo_objeto']}'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        obj = model.objects.filter(pk=data['objeto_id']).first()
        if obj is None:
            return Response(
                {'error': f"Objeto no encontrado: {data['tipo_objeto']}#{data['objeto_id']}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        service = ReferenciaService()
        ref = service.crear(
            url=data['url'],
            nombre=data['nombre'],
            categoria=data.get('categoria', 'OTRO'),
            content_object=obj,
            creado_por=request.user,
            descripcion=data.get('descripcion', ''),
            orden=data.get('orden', 0),
        )
        return Response(ReferenciaSerializer(ref).data, status=status.HTTP_201_CREATED)


class ReferenciaBulkView(APIView):
    """POST /api-repo/referencias/bulk/"""

    def post(self, request):
        serializer = ReferenciaBulkRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        model = get_modelo(data['tipo_objeto'])
        if model is None:
            return Response(
                {'error': f"Tipo de objeto no permitido: '{data['tipo_objeto']}'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        obj = model.objects.filter(pk=data['objeto_id']).first()
        if obj is None:
            return Response(
                {'error': f"Objeto no encontrado: {data['tipo_objeto']}#{data['objeto_id']}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        service = ReferenciaService()
        refs = service.crear_bulk(
            referencias_data=data['referencias'],
            content_object=obj,
            creado_por=request.user,
        )
        return Response(ReferenciaSerializer(refs, many=True).data, status=status.HTTP_201_CREATED)


class ReferenciaDeleteView(APIView):
    """DELETE /api-repo/referencias/{id}/"""

    def delete(self, request, referencia_id):
        service = ReferenciaService()
        ref = service.obtener_por_id(referencia_id)
        if ref is None:
            return Response(
                {'error': f"Referencia no encontrada: {referencia_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        service.eliminar(ref)
        return Response({'mensaje': 'Referencia eliminada'}, status=status.HTTP_200_OK)