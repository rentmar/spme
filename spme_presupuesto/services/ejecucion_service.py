#spme/spme_presupuesto/services/ejecucion_service.py
from spme_actividades.models import Actividad, TareaActividad
from spme_presupuesto.repositories.ejecucion_repository import EjecucionRepository


class EjecucionService:
    """
    Logica de negocio para consulta de ejecucion presupuestaria
    """
    def __init__(self, repository=None):
        self.repository = repository or EjecucionRepository
    
    def detalle_ejecucion_actividad(self, actividad_id):
        """
        Obtiene el detalle de ejecución de una actividad.
        
        Incluye solicitudes directas y solicitudes de cada tarea.
        """

        actividad = Actividad.objects.get(id=actividad_id)

        #Solicitudes directas de la actividad
        todas_solicitudes = self.repository.obtener_solicitudes_aprobadas_actividad(actividad_id)
        solicitudes_directas = [s for s in todas_solicitudes if s['es_directa']]

        # Agrupar solicitudes por tarea
        tareas_data = []
        for tarea in actividad.tareas.all():
            solicitudes_tarea = [s for s in todas_solicitudes if s['tarea_id'] == tarea.id]
            ejecutado_tarea = sum(s['monto'] for s in solicitudes_tarea)

            tareas_data.append({
                'tarea_id': tarea.id,
                'tarea_codigo': tarea.codigo or '',
                'tarea_titulo': tarea.titulo or 'Sin título',
                'ejecutado': ejecutado_tarea,
                'solicitudes': solicitudes_tarea,
            })
        
        total_ejecutado = self.repository.total_ejecutado_actividad(actividad_id)
        presupuesto = float(actividad.presupuesto or 0)

        return {
            'actividad_id': actividad.id,
            'actividad_codigo': actividad.codigo or '',
            'actividad_nombre': actividad.nombreCorto or '',
            'presupuesto': presupuesto,
            'ejecutado': sum(s['monto'] for s in solicitudes_directas),
            'solicitudes_directas': solicitudes_directas,
            'tareas': tareas_data,
            'total_ejecutado': total_ejecutado,
            'saldo': presupuesto - total_ejecutado,
            'porcentaje_ejecucion': (
                f"{round((total_ejecutado / presupuesto * 100), 2)}%"
                if presupuesto > 0 else "0%"
            ),
        }
    
    def detalle_ejecucion_tarea(self, tarea_id):
        """
        Obtiene el detalle de ejecución de una tarea.
        """
        tarea = TareaActividad.objects.get(id=tarea_id)
        solicitudes = self.repository.obtener_solicitudes_aprobadas_tarea(tarea_id)
        total_ejecutado = sum(s['monto'] for s in solicitudes)

        return {
            'tarea_id': tarea.id,
            'tarea_codigo': tarea.codigo or '',
            'tarea_titulo': tarea.titulo or 'Sin título',
            'presupuesto': float(tarea.presupuesto or 0),
            'ejecutado': total_ejecutado,
            'solicitudes': solicitudes,
        }
