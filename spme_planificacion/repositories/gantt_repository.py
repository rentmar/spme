# spme_planificacion/repositories/gantt_repository.py
from spme_estructuracion_proyecto.models import Proyecto
from spme_actividades.models import Actividad, TareaActividad
# spme_planificacion/repositories/gantt_repository.py

class GanttRepository:

    @staticmethod
    def get_proyectos():
        return Proyecto.objects.filter(esta_habilitado=True, fecha_inicio__isnull=False).order_by('fecha_inicio')

    @staticmethod
    def get_actividades(proyecto_ids):
        return Actividad.objects.filter(
            proyecto_id__in=proyecto_ids,
            estaInactiva=False
        ).select_related('proyecto').order_by('fecha_inicio')

    @staticmethod
    def get_tareas(actividad_ids):
        return TareaActividad.objects.filter(
            actividad_id__in=actividad_ids
        ).select_related('actividad').order_by('fecha_creacion')