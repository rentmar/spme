#spme/spme_presupuesto/services/balance_service.py
from spme_estructuracion_proyecto.models import Proyecto
from spme_presupuesto.repositories.planificacion_repository import PlanificacionRepository
from spme_presupuesto.repositories.ejecucion_repository import EjecucionRepository


class BalanceService:
    """
    Logica de negocios para el balance economico comparativo
    """
    def __init__(self, plan_repo=None, ejec_repo=None):
        self.plan_repo = plan_repo or PlanificacionRepository()
        self.ejec_repo = ejec_repo or EjecucionRepository()

    def balance_proyecto(self, proyecto_id):
        """
        Balance completo del proyecto: planificado vs ejecutado
        """
        proyecto = Proyecto.objects.get(id=proyecto_id)
        actividades = self.plan_repo.obtener_actividad_planificadas(proyecto_id)
        actividades_balance = []

        for act in actividades:
            ejecutado = self.ejec_repo.total_ejecutado_actividad(act.id)
            presupuesto = float(act.presupuesto or 0)
            num_tareas = act.tareas.count()
            tareas_completadas = act.tareas.filter(estado='COMPL').count()

            actividades_balance.append({
                'codigo': act.codigo or '',
                'nombre': act.nombreCorto or '',
                'estado': act.estado,
                'planificado': presupuesto,
                'ejecutado': ejecutado,
                'diferencia': ejecutado - presupuesto,
                'porcentaje_desviacion': (
                    round(((ejecutado - presupuesto) / presupuesto * 100), 2)
                    if presupuesto > 0 else 0
                ),
                'grado_ejecucion': (
                    f"{round((ejecutado / presupuesto * 100), 2)}%"
                    if presupuesto > 0 else "0%"
                ),
                'saldo': presupuesto - ejecutado,
                'num_tareas': num_tareas,
                'tareas_completadas': tareas_completadas,
            })
        
        total_plan = sum(a['planificado'] for a in actividades_balance)
        total_ejec = sum(a['ejecutado'] for a in actividades_balance)

        mensajes = {
            'ES': 'Proyecto en estructuración.',
            'EP': 'Proyecto en planificación. Ejecutado en cero.',
            'PL': 'Proyecto planificado. Ejecutado en cero.',
            'EJ': 'Proyecto en ejecución. Balance completo.',
        }

        return {
            'proyecto_codigo': proyecto.codigo,
            'proyecto_titulo': proyecto.titulo,
            'proyecto_estado': proyecto.estado,
            'proyecto_estado_display': proyecto.get_estado_display(),
            'presupuesto_proyecto': total_plan,
            'total_ejecutado': total_ejec,
            'saldo_global': total_plan - total_ejec,
            'porcentaje_ejecucion_global': (
                round((total_ejec / total_plan * 100), 2)
                if total_plan > 0 else 0
            ),
            'actividades': actividades_balance,
            'deficit_superavit_caja': total_ejec - total_ejec,
            'conciliacion': 0,
            'mensaje': mensajes.get(proyecto.estado, ''),
        }
    
    def balance_actividad(self, actividad_id):
        """
        Balance de una actividad especifica
        """
        proyecto_id = self._get_proyecto_id(actividad_id)
        balance = self.balance_proyecto(proyecto_id)
        
        for act in balance['actividades']:
            from spme_actividades.models import Actividad
            actividad = Actividad.objects.get(id=actividad_id)
            if act['codigo'] == actividad.codigo:
                return act
            
        return None
    
    def balance_tarea(self, tarea_id):
        """
        Balance de una tarea especifica
        """
        from spme_actividades.models import TareaActividad
        tarea = TareaActividad.objects.get(id=tarea_id)
        ejecutado = self.ejec_repo.total_ejecutado_tarea(tarea_id)
        presupuesto = float(tarea.presupuesto or 0)

        return {
            'tarea_id': tarea.id,
            'tarea_codigo': tarea.codigo or '',
            'tarea_titulo': tarea.titulo or 'Sin título',
            'planificado': presupuesto,
            'ejecutado': ejecutado,
            'diferencia': ejecutado - presupuesto,
            'porcentaje_desviacion': (
                round(((ejecutado - presupuesto) / presupuesto * 100), 2)
                if presupuesto > 0 else 0
            ),
        }
    
    def _get_proyecto_id(self, actividad_id):
        from spme_actividades.models import Actividad
        return Actividad.objects.get(id=actividad_id).proyecto_id