# spme/apptran/proyecto/views/actividad_solicitudes_view.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..services.actividad_solicitudes_service import ActividadSolicitudesService

from ..serializers.actividad_solicitudes_serializer import (
    ActividadSolicitudesResponseSerializer
)

class ActividadSolicitudesView(APIView):
    """
    Endpoint que devuelve actividades con tareas y badges de solicitudes.
    
    GET /api/v2/actividades/solicitudes/
    Parámetros:
        - page: número de página (default: 1)
        - page_size: items por página (default: 20, max: 100)
        - search: búsqueda por código o nombre corto
        - estado: filtrar por estado (PLAN,EJEC,FIN)
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ActividadSolicitudesService()

    def get(self, request):
        try:
            # Parámetros de paginación
            page = int(request.query_params.get('page', 1))
            page_size = min(
                int(request.query_params.get('page_size', 20)),
                100  # Límite máximo
            )

            # Filtros
            filtros = {}
            search = request.query_params.get('search', '').strip()
            estado = request.query_params.get('estado', '').strip()

            if search:
                filtros['search'] = search
            if estado:
                filtros['estado'] = estado

            # Obtener datos
            data = self.service.obtener_actividades(
                usuario=request.user,
                filtros=filtros if filtros else None,
                page=page,
                page_size=page_size,
            )

            # Construir y validar respuesta
            response_data = {
                'success': True,
                **data,
            }

            serializer = ActividadSolicitudesResponseSerializer(data=response_data)
            serializer.is_valid(raise_exception=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response(
                {'success': False, 'error': f'Parámetro inválido: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )