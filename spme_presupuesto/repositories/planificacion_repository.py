# spme/spme_presupuesto/repositories/planificacion_repository.py
from django.db.models import Sum
from spme_estructuracion_proyecto.models import Proyecto
from spme_actividades.models import Actividad, TareaActividad


class PlanificacionRepository:
    """
    Consultas de datos planificados

    Esta clase encapsula todo el acceso a datos para el módulo de planificación.
    Ninguna otra capa debe hacer consultas ORM directamente.
    """

    @staticmethod
    def obtener_proyecto(proyecto_id):
        """
        Obtiene un proyecto por su ID

        Args:
            proyecto_id: ID del proyecto
            
        Returns:
            Proyecto o None si no existe
        
        Raises:
            Proyecto.DoesNotExist si no se encuentra
        """
        return Proyecto.objects.get(id=proyecto_id)
    
    @staticmethod
    def obtener_actividad_planificadas(proyecto_id):
        """
        Obtiene las actividades activas con presupuesto planificado
        
        Args:
            proyecto_id: ID del proyecto
            
        Returns:
            QuerySet de Actividad ordenadas por fecha_programada

        """
        return Actividad.objects.filter(
            proyecto_id=proyecto_id,
            estaInactiva=False
        ).order_by('fecha_programada')
    
    @staticmethod
    def obtener_tareas_planificadas(actividad_id):
        """
        Obtiene las tareas de una actividad ordenadas por fecha de creación.

        Args:
            actividad_id: ID de la actividad
            
        Returns:
            QuerySet de TareaActividad
        """
        return TareaActividad.objects.filter(
            actividad_id=actividad_id
        ).order_by('fecha_creacion')
    
    @staticmethod
    def total_planificado_actividades(proyecto_id):
        """
        Calcula la suma del presupuesto de todas las actividades activas.
        
        Args:
            proyecto_id: ID del proyecto
            
        Returns:
            Decimal con la suma total, 0 si no hay actividades
        """
        return Actividad.objects.filter(
            proyecto_id=proyecto_id,
            estaInactiva=False
        ).aggregate(total=Sum('presupuesto'))['total'] or 0