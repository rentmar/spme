# spme/apptran/proyecto/repositories/actividad_repository.py
from spme_actividades.models import Actividad

class ActividadRepository:

    def get_actividad_por_id(idactividad):
        return Actividad.objects.select_related(
            'tipo', 'proyecto', 'responsable'
        ).prefetch_related(
            'tareas',
            'proyecto__instancia_gestora',
            'proyecto__procedencia_fondos',
        ).filter(pk=idactividad, estaInactiva=False).first()