"""
Vistas para el buscador global de adjuntos y referencias.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.paginator import Paginator

from spme_repositorio.serializers.busqueda_serializers import BusquedaResponseSerializer
from spme_repositorio.services.busqueda.busqueda_service import BusquedaService


class BuscadorGlobalView(APIView):
    """
    GET /api-repo/repositorio/buscar/
    
    Busca adjuntos y referencias en todos los proyectos.
    
    Parámetros:
        - tipo: 'adjuntos' | 'referencias' (obligatorio)
        - q: texto de búsqueda
        - tipo_archivo: DOCUMENTO | IMAGEN | AUDIO | VIDEO | OTRO
        - categoria: youtube | drive | facebook | etc.
        - proyecto_id: filtrar por proyecto
        - fecha_desde: YYYY-MM-DD
        - fecha_hasta: YYYY-MM-DD
        - pagina: número de página (default 1)
        - por_pagina: resultados por página (default 20)
    """

    def get(self, request):
        # 1. Obtener parámetros
        tipo = request.GET.get('tipo', 'adjuntos').lower()
        query = request.GET.get('q', '').strip()
        tipo_archivo = request.GET.get('tipo_archivo', '').strip()
        categoria = request.GET.get('categoria', '').strip()
        proyecto_id_str = request.GET.get('proyecto_id', '').strip()
        fecha_desde = request.GET.get('fecha_desde', '').strip()
        fecha_hasta = request.GET.get('fecha_hasta', '').strip()
        
        try:
            pagina = int(request.GET.get('pagina', 1))
            por_pagina = int(request.GET.get('por_pagina', 20))
        except ValueError:
            return Response(
                {'error': 'pagina y por_pagina deben ser números'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2. Validar tipo
        if tipo not in ['adjuntos', 'referencias']:
            return Response(
                {'error': "tipo debe ser 'adjuntos' o 'referencias'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 3. Convertir proyecto_id
        proyecto_id = None
        if proyecto_id_str:
            try:
                proyecto_id = int(proyecto_id_str)
            except ValueError:
                return Response(
                    {'error': 'proyecto_id debe ser un número'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # 4. Ejecutar búsqueda
        service = BusquedaService()
        
        if tipo == 'adjuntos':
            resultados = service.buscar_adjuntos(
                query=query,
                tipo_archivo=tipo_archivo,
                proyecto_id=proyecto_id,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
            )
        else:
            resultados = service.buscar_referencias(
                query=query,
                categoria=categoria,
                proyecto_id=proyecto_id,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
            )

        # 5. Paginación
        paginator = Paginator(resultados, por_pagina)
        pagina_obj = paginator.get_page(pagina)

        response_data = {
            'total': paginator.count,
            'pagina': pagina_obj.number,
            'por_pagina': por_pagina,
            'total_paginas': paginator.num_pages,
            'tipo': tipo,
            'resultados': list(pagina_obj.object_list),
        }

        # 6. Serializar
        serializer = BusquedaResponseSerializer(data=response_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data)