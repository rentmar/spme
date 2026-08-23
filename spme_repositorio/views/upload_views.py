# spme/spme_repositorio/views/upload_views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from spme_repositorio.serializers.upload_serializers import (
    AdjuntoSerializer,
    FallidoSerializer,
)
from spme_repositorio.services.storage.adjunto_service import AdjuntoService
from spme_repositorio.nodos_config import get_modelo


class UploadArchivoView(APIView):
    """
    POST /api-repo/repositorio/upload/
    
    Sube múltiples archivos a Garage y crea adjuntos asociados.
    Acepta multipart/form-data con:
        - tipo_objeto: string (ej: 'indicadorog', 'actividad', 'tarea')
        - objeto_id: integer
        - descripcion: string (opcional)
        - archivos: uno o más archivos
    """
    parser_classes = [MultiPartParser, FormParser]

    def _get_content_object(self, tipo_objeto: str, objeto_id: int):
        model = get_modelo(tipo_objeto)
        if model is None:
            return None, 400, f"Tipo de objeto no permitido: '{tipo_objeto}'"
        obj = model.objects.filter(pk=objeto_id).first()
        if obj is None:
            return None, 404, f"Objeto no encontrado: {tipo_objeto}#{objeto_id}"
        return obj, None, None

    def _verificar_permiso(self, user, content_object) -> bool:
        # TODO: Implementar verificación de permisos real
        return True

    def post(self, request):
        # ================================================================
        # 1. Obtener archivos directamente de request.FILES
        # ================================================================
        archivos = request.FILES.getlist('archivos')
        
        if not archivos:
            return Response(
                {'error': 'No se proporcionaron archivos'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ================================================================
        # 2. Obtener y validar campos
        # ================================================================
        tipo_objeto = request.POST.get('tipo_objeto', '').strip()
        objeto_id_str = request.POST.get('objeto_id', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()

        if not tipo_objeto:
            return Response(
                {'error': 'tipo_objeto es requerido'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not objeto_id_str:
            return Response(
                {'error': 'objeto_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            objeto_id = int(objeto_id_str)
        except ValueError:
            return Response(
                {'error': 'objeto_id debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if objeto_id < 1:
            return Response(
                {'error': 'objeto_id debe ser mayor a 0'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ================================================================
        # 3. Resolver content_object
        # ================================================================
        content_object, error_code, error_message = self._get_content_object(
            tipo_objeto, objeto_id
        )

        if content_object is None:
            return Response({'error': error_message}, status=error_code)

        # ================================================================
        # 4. Verificar permisos
        # ================================================================
        if not self._verificar_permiso(request.user, content_object):
            return Response(
                {'error': 'No tiene permisos para modificar este objeto'},
                status=status.HTTP_403_FORBIDDEN,
            )

        # ================================================================
        # 5. Subir archivos
        # ================================================================
        service = AdjuntoService()
        resultado = service.subir_multiples_y_asociar(
            files=archivos,
            tipo_objeto=tipo_objeto,
            content_object=content_object,
            creado_por=request.user,
            descripcion=descripcion,
        )

        # ================================================================
        # 6. Construir respuesta
        # ================================================================
        response_data = {
            'exitosos': AdjuntoSerializer(resultado.exitosos, many=True).data,
            'fallidos': FallidoSerializer(
                [
                    {'nombre_original': f.nombre_original, 'error': f.error}
                    for f in resultado.fallidos
                ],
                many=True,
            ).data,
            'total': resultado.total,
            'todos_exitosos': resultado.todos_exitosos,
        }

        response_status = (
            status.HTTP_201_CREATED
            if resultado.todos_exitosos
            else status.HTTP_207_MULTI_STATUS
        )
        return Response(response_data, status=response_status)


class AdjuntosObjetoView(APIView):
    """
    GET /api-repo/repositorio/adjuntos/{tipo_objeto}/{objeto_id}/
    """

    def get(self, request, tipo_objeto, objeto_id):
        model = get_modelo(tipo_objeto)
        if model is None:
            return Response(
                {'error': f"Tipo de objeto no permitido: '{tipo_objeto}'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        content_object = model.objects.filter(pk=objeto_id).first()
        if content_object is None:
            return Response(
                {'error': f'Objeto no encontrado: {tipo_objeto}#{objeto_id}'},
                status=status.HTTP_404_NOT_FOUND,
            )

        service = AdjuntoService()
        adjuntos = service.obtener_adjuntos(content_object)
        serializer = AdjuntoSerializer(adjuntos, many=True)
        return Response(serializer.data)


class EliminarAdjuntoView(APIView):
    """
    DELETE /api-repo/repositorio/adjuntos/{adjunto_id}/
    
    Elimina un adjunto. Si el archivo no tiene más asociaciones,
    lo elimina también de Garage y MySQL.
    """

    def delete(self, request, adjunto_id):
        from spme_repositorio.models import Adjunto

        adjunto = Adjunto.objects.filter(pk=adjunto_id).first()

        if adjunto is None:
            return Response(
                {'error': f'Adjunto no encontrado: {adjunto_id}'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # TODO: Verificar permisos sobre el objeto dueño
        # if not usuario_puede_modificar(request.user, adjunto.content_object):
        #     return Response({'error': 'Sin permisos'}, status=403)

        try:
            service = AdjuntoService()
            service.eliminar_adjunto_y_archivo(adjunto)
            return Response(
                {'mensaje': f'Adjunto {adjunto_id} eliminado correctamente'},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {'error': f'Error al eliminar adjunto: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )