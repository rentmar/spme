"""
Servicio para búsqueda global de adjuntos y referencias.
Contiene la lógica de negocio para resolver proyectos y nodos.
"""

import logging
from typing import Dict, List, Optional

from spme_repositorio.repositories.busqueda.busqueda_repository import BusquedaRepository

logger = logging.getLogger(__name__)


class BusquedaService:
    """Servicio de búsqueda global."""

    # Mapeo de nombre del modelo Django → nodo_tipo del árbol
    MAPA_TIPO_NODO = {
        'indicadorobjetivogeneral': 'indicadorog',
        'indicadorresultadoobjgral': 'indicadorrog',
        'indicadorobjetivoespecifico': 'indicadoroe',
        'indicadorresultadoobjespecifico': 'indicadorroe',
        'actividad': 'actividad',
        'tareaactividad': 'tarea',
        'productooe': 'productooe',
        'productoresultadooe': 'productoroe',
        'resultadoog': 'resultadoog',
        'resultadooe': 'resultadooe',
        'solicitudfondos': 'solicitudfondosact',
    }

    def __init__(self):
        self._repo = BusquedaRepository()

    def buscar_adjuntos(
        self,
        query: str = '',
        tipo_archivo: str = '',
        proyecto_id: Optional[int] = None,
        fecha_desde: str = '',
        fecha_hasta: str = '',
    ) -> List[Dict]:
        """Busca adjuntos y construye resultados con información de proyecto."""
        adjuntos = self._repo.buscar_adjuntos(
            query=query,
            tipo_archivo=tipo_archivo,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )

        resultados = []
        for adjunto in adjuntos:
            nodo = adjunto.content_object
            proyecto = self._obtener_proyecto(nodo)

            if proyecto_id and proyecto and proyecto.id != proyecto_id:
                continue

            resultados.append({
                'id': adjunto.id,
                'tipo_resultado': 'adjunto',
                'nombre': adjunto.archivo.nombre_original,
                'tipo_archivo': adjunto.archivo.tipo_archivo,
                'mime_type': adjunto.archivo.mime_type,
                'tamano': adjunto.archivo.tamano,
                'descripcion': adjunto.descripcion or '',
                'fecha_creacion': adjunto.creado_en,
                'archivo_id': adjunto.archivo.id,
                'adjunto_id': adjunto.id,
                'proyecto': self._serializar_proyecto(proyecto),
                'nodo': self._serializar_nodo(nodo, adjunto.content_type.model),
            })

        return resultados

    def buscar_referencias(
        self,
        query: str = '',
        categoria: str = '',
        proyecto_id: Optional[int] = None,
        fecha_desde: str = '',
        fecha_hasta: str = '',
    ) -> List[Dict]:
        """Busca referencias y construye resultados con información de proyecto."""
        referencias = self._repo.buscar_referencias(
            query=query,
            categoria=categoria,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )

        resultados = []
        for referencia in referencias:
            nodo = referencia.content_object
            proyecto = self._obtener_proyecto(nodo)

            if proyecto_id and proyecto and proyecto.id != proyecto_id:
                continue

            resultados.append({
                'id': referencia.id,
                'tipo_resultado': 'referencia',
                'nombre': referencia.nombre,
                'categoria': referencia.categoria,
                'url': referencia.url,
                'descripcion': referencia.descripcion or '',
                'fecha_creacion': referencia.creado_en,
                'referencia_id': referencia.id,
                'proyecto': self._serializar_proyecto(proyecto),
                'nodo': self._serializar_nodo(nodo, referencia.content_type.model),
            })

        return resultados

    def _obtener_proyecto(self, nodo):
        """Recorre la jerarquía del nodo hasta encontrar el proyecto."""
        if nodo is None:
            return None

        try:
            # Actividad → Proyecto (directo)
            if hasattr(nodo, 'proyecto') and nodo.proyecto:
                return nodo.proyecto

            # Tarea → Actividad → Proyecto
            if hasattr(nodo, 'actividad') and nodo.actividad:
                if nodo.actividad.proyecto:
                    return nodo.actividad.proyecto

            # IndicadorObjetivoGeneral → ObjetivoGeneral → Proyecto
            if hasattr(nodo, 'objetivo_general') and nodo.objetivo_general:
                if nodo.objetivo_general.proyecto:
                    return nodo.objetivo_general.proyecto

            # ResultadoOG → ObjetivoGeneral → Proyecto
            if hasattr(nodo, 'resultado_og') and nodo.resultado_og:
                if nodo.resultado_og.objetivo_general:
                    if nodo.resultado_og.objetivo_general.proyecto:
                        return nodo.resultado_og.objetivo_general.proyecto

            # ObjetivoEspecifico → Proyecto
            if hasattr(nodo, 'objetivo_especifico') and nodo.objetivo_especifico:
                if nodo.objetivo_especifico.proyecto:
                    return nodo.objetivo_especifico.proyecto

            # ResultadoOE → ObjetivoEspecifico → Proyecto
            if hasattr(nodo, 'resultado_obj_especifico') and nodo.resultado_obj_especifico:
                if nodo.resultado_obj_especifico.objetivo_especifico:
                    if nodo.resultado_obj_especifico.objetivo_especifico.proyecto:
                        return nodo.resultado_obj_especifico.objetivo_especifico.proyecto

            # ProductoOE → ObjetivoEspecifico → Proyecto
            if hasattr(nodo, 'objetivo_especifico') and nodo.objetivo_especifico:
                if nodo.objetivo_especifico.proyecto:
                    return nodo.objetivo_especifico.proyecto

            # ProductoResultadoOE → ResultadoOE → ObjetivoEspecifico → Proyecto
            if hasattr(nodo, 'resultado_oe') and nodo.resultado_oe:
                if nodo.resultado_oe.objetivo_especifico:
                    if nodo.resultado_oe.objetivo_especifico.proyecto:
                        return nodo.resultado_oe.objetivo_especifico.proyecto

        except Exception as e:
            logger.debug(f"Error obteniendo proyecto para nodo {nodo}: {e}")

        return None

    def _serializar_proyecto(self, proyecto) -> Optional[Dict]:
        if not proyecto:
            return None
        return {
            'id': proyecto.id,
            'nombre': proyecto.titulo,
            'codigo': proyecto.codigo,
        }

    def _serializar_nodo(self, nodo, tipo_modelo) -> Optional[Dict]:
        if not nodo:
            return None
        
        # Mapear nombre del modelo Django a nodo_tipo del árbol
        tipo_arbol = self.MAPA_TIPO_NODO.get(tipo_modelo, tipo_modelo)
        
        return {
            'id': nodo.id,
            'tipo': tipo_arbol,
            'nombre': str(nodo),
            'codigo': getattr(nodo, 'codigo', None),
        }