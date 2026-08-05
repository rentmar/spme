# spme/apptran/proyecto/services/actividad_solicitudes_service.py
# api/v2/services/actividad_solicitudes_service.py
from django.core.paginator import Paginator
from ..repositories.actividad_solicitudes_repository import ActividadSolicitudesRepository

class ActividadSolicitudesService:
    """Servicio para actividades con solicitudes."""

    def __init__(self):
        self.repository = ActividadSolicitudesRepository()

    def obtener_actividades(self, usuario, filtros=None, page=1, page_size=20):
        """
        Obtiene lista paginada de actividades con tareas y badges.
        """
        queryset = self.repository.get_actividades_con_tareas(
            usuario=usuario, filtros=filtros
        )

        paginator = Paginator(queryset, page_size)
        pagina = paginator.get_page(page)

        resultados = []
        for actividad in pagina:
            data = self._serializar_actividad(actividad)
            resultados.append(data)

        return {
            'results': resultados,
            'pagination': {
                'count': paginator.count,
                'page': pagina.number,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
            },
        }

    def _serializar_actividad(self, actividad):
        """Convierte una actividad al formato de respuesta."""
        return {
            'id': actividad.id,
            'codigo': actividad.codigo or '',
            'nombre_corto': actividad.nombreCorto or '',
            'descripcion': actividad.descripcion or '',
            'estado': actividad.estado,
            'presupuesto': float(actividad.presupuesto or 0),
            'procedencia_fondos': actividad.procedencia_fondos,
            'fecha_programada': (
                actividad.fecha_programada.isoformat()
                if actividad.fecha_programada else None
            ),
            'duracion': (
                (actividad.fecha_cierre - actividad.fecha_inicio).days
                if actividad.fecha_inicio and actividad.fecha_cierre else None
            ),
            'fecha_inicio': (
                actividad.fecha_inicio.isoformat()
                if actividad.fecha_inicio else None
            ),
            'fecha_cierre': (
                actividad.fecha_cierre.isoformat()
                if actividad.fecha_cierre else None
            ),
            'responsable': (
                {
                    'id': actividad.responsable.id,
                    'nombre': actividad.responsable.get_full_name(),
                }
                if actividad.responsable else None
            ),
            'proyecto': (
                {
                    'id': actividad.proyecto.id,
                    'nombre': actividad.proyecto.titulo,
                }
                if actividad.proyecto else None
            ),
            'badges': self.repository.get_badges_actividad(actividad.id),
            'tareas': [
                self._serializar_tarea(tarea)
                for tarea in actividad.tareas.all()
            ],
        }

    def _serializar_tarea(self, tarea):
        """Convierte una tarea al formato de respuesta."""
        return {
            'id': tarea.id,
            'titulo': tarea.titulo or '',
            'descripcion': tarea.descripcion or '',
            'estado': tarea.estado,
            'codigo': tarea.codigo or '',
            'badges': self.repository.get_badges_tarea(tarea.id),
        }