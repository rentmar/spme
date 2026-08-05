# spme_planificacion/services/gantt_service.py
# spme_planificacion/services/gantt_service.py
from ..repositories.gantt_repository import GanttRepository
from ..serializers.gantt_serializers import ProyectoGanttSerializer, ActividadGanttSerializer, TareaGanttSerializer

class GanttService:

    def get_gantt_data(self):
        proyectos = GanttRepository.get_proyectos()
        proyectos_data = ProyectoGanttSerializer(proyectos, many=True).data
        
        proyecto_ids = [p.id for p in proyectos]
        actividades = GanttRepository.get_actividades(proyecto_ids)
        actividades_data = ActividadGanttSerializer(actividades, many=True).data
        
        actividad_ids = [a.id for a in actividades]
        tareas = GanttRepository.get_tareas(actividad_ids)
        tareas_data = TareaGanttSerializer(tareas, many=True).data
        
        data = proyectos_data + actividades_data + tareas_data
        return {'data': data}