from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..services.actividad_rendiciones_service import ActividadRendicionesService

class ActividadRendicionesView(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ActividadRendicionesService()

    def get(self, request):
        try:
            page = int(request.query_params.get('page', 1))
            page_size = min(int(request.query_params.get('page_size', 20)), 100)
            filtros = {}
            search = request.query_params.get('search', '').strip()
            estado = request.query_params.get('estado', '').strip()
            if search: filtros['search'] = search
            if estado: filtros['estado'] = estado

            data = self.service.obtener_actividades(request.user, filtros if filtros else None, page, page_size)
            return Response({'success': True, **data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)