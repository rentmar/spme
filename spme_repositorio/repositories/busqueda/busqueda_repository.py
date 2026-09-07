"""
Repositorio para búsqueda global de adjuntos y referencias.
Acceso a datos puro, sin lógica de negocio.
"""

from django.db.models import Q
from spme_repositorio.models import Adjunto, ReferenciaExterna


class BusquedaRepository:
    """Repositorio para consultas de búsqueda global."""

    def buscar_adjuntos(
        self,
        query: str = '',
        tipo_archivo: str = '',
        fecha_desde: str = '',
        fecha_hasta: str = '',
    ):
        """Busca adjuntos con filtros."""
        adjuntos = Adjunto.objects.select_related('archivo', 'content_type')

        if query:
            adjuntos = adjuntos.filter(
                Q(archivo__nombre_original__icontains=query) |
                Q(descripcion__icontains=query)
            )

        if tipo_archivo:
            adjuntos = adjuntos.filter(archivo__tipo_archivo=tipo_archivo)

        if fecha_desde:
            adjuntos = adjuntos.filter(creado_en__date__gte=fecha_desde)
        if fecha_hasta:
            adjuntos = adjuntos.filter(creado_en__date__lte=fecha_hasta)

        return adjuntos

    def buscar_referencias(
        self,
        query: str = '',
        categoria: str = '',
        fecha_desde: str = '',
        fecha_hasta: str = '',
    ):
        """Busca referencias externas con filtros."""
        referencias = ReferenciaExterna.objects.select_related('content_type')

        if query:
            referencias = referencias.filter(
                Q(nombre__icontains=query) |
                Q(url__icontains=query) |
                Q(descripcion__icontains=query)
            )

        if categoria:
            referencias = referencias.filter(categoria=categoria)

        if fecha_desde:
            referencias = referencias.filter(creado_en__date__gte=fecha_desde)
        if fecha_hasta:
            referencias = referencias.filter(creado_en__date__lte=fecha_hasta)

        return referencias