#spme/apptran/proyecto/repositories/proyecto_repository.py
from django.db.models import Prefetch
from spme_actividades.models import Actividad, TareaActividad
from spme_estructuracion_proyecto.models import Proyecto

class ProyectoRepository:
    """
    Repositorio para consultas relacionadas con Proyectos
    """
    
    @staticmethod
    def get_proyecto_con_estructura_completa(proyecto_id):
        """
        Obtiene un proyecto con todas sus relaciones necesarias
        """
        try:
            proyecto = Proyecto.objects.prefetch_related(
                Prefetch(
                    'actividad_proyecto',
                    queryset=Actividad.objects.filter(
                        estaInactiva=False
                    ).prefetch_related(
                        Prefetch(
                            'tareas',
                            queryset=TareaActividad.objects.all().order_by(
                                'fecha_creacion', 'codigo'
                            )
                        )
                    ).order_by('fecha_programada', 'codigo')
                ),
                'instancia_gestora',
                'procedencia_fondos'
            ).select_related(
                'propietario',
                'pei',
                'programa'
            ).get(
                id=proyecto_id,
                esta_habilitado=True
            )
            
            return proyecto
            
        except Proyecto.DoesNotExist:
            return None
    
    @staticmethod
    def get_proyecto_por_id(proyecto_id):
        """
        Obtiene un proyecto por su ID
        """
        try:
            return Proyecto.objects.get(
                id=proyecto_id, 
                esta_habilitado=True
            )
        except Proyecto.DoesNotExist:
            return None
    
    @staticmethod
    def get_actividades_con_tareas(proyecto_id):
        """
        Obtiene las actividades de un proyecto con sus tareas
        VERSIÓN CORREGIDA - Misma consulta que en la estructura completa
        """
        # Primero obtener el proyecto
        try:
            proyecto = Proyecto.objects.get(id=proyecto_id, esta_habilitado=True)
        except Proyecto.DoesNotExist:
            return Actividad.objects.none()
        
        # Usar el related_name igual que en el serializador
        actividades = proyecto.actividad_proyecto.filter(
            estaInactiva=False
        ).prefetch_related(
            'tareas'
        ).order_by('fecha_programada', 'codigo')
        
        return actividades