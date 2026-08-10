from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import StreamingHttpResponse

from spme_repositorio.services.storage.garage_service import GarageService
from spme_repositorio.models import Archivo


class DescargarArchivoView(APIView):
    """
    GET /api-repo/repositorio/descargar/{archivo_id}/
    
    Descarga un archivo desde Garage usando StreamingHttpResponse.
    Django no carga el archivo completo en memoria.
    """

    def get(self, request, archivo_id):
        archivo = Archivo.objects.filter(pk=archivo_id).first()

        if archivo is None:
            return Response(
                {'error': f'Archivo no encontrado: {archivo_id}'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # TODO: Verificar permisos sobre el objeto dueño del Adjunto
        # adjunto = archivo.adjuntos.first()
        # if not usuario_puede_descargar(request.user, adjunto.content_object):
        #     return Response({'error': 'Sin permisos'}, status=403)

        service = GarageService()
        resultado = service.descargar(archivo.key)
        body = resultado['body']

        response = StreamingHttpResponse(
            self._generar_chunks(body),
            content_type=archivo.mime_type,
        )
        response['Content-Length'] = str(archivo.tamano)
        response['Content-Disposition'] = f'attachment; filename="{archivo.nombre_original}"'
        return response

    def _generar_chunks(self, body, chunk_size=64 * 1024):
        """
        Genera chunks del stream desde Garage.
        
        Lee de a 64 KB y envía progresivamente al navegador.
        Cierra el stream al finalizar.
        """
        try:
            while True:
                chunk = body.read(chunk_size)
                if not chunk:
                    break
                yield chunk
        finally:
            body.close()