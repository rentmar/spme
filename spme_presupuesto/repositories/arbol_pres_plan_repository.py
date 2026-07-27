# spme_presupuesto/repositories/arbol_pres_plan_repository.py

from spme_estructuracion_proyecto.models import Proyecto

class ArbolPresPlanRepository:
    """
    Repositorio para el árbol de presupuesto planificado.
    Responsabilidad: Acceso a datos del proyecto.
    """
    
    def obtener_proyecto(self, proyecto_id):
        """
        Obtiene el proyecto con todas sus relaciones necesarias.
        
        Args:
            proyecto_id (int): ID del proyecto
            
        Returns:
            Proyecto: Instancia del proyecto con relaciones cargadas
            
        Raises:
            Proyecto.DoesNotExist: Si el proyecto no existe
        """
        return Proyecto.objects.select_related(
            'propietario',
            'pei',
            'programa'
        ).prefetch_related(
            'instancia_gestora',
            'procedencia_fondos',
            'actividad_proyecto',
        ).get(id=proyecto_id)