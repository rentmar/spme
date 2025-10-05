from spme_estructuracion_proyecto.models import Proyecto

class ProyectoRepository:
    @staticmethod
    def get_full_proyecto(proyecto_id):
        return (
            Proyecto.objects
            .select_related('pei', 'programa')
            .prefetch_related(
                'instancia_gestora',
                'procedencia_fondos',
                'objetivo_general',
                'objetivos_especificos',
            )
            .filter(id=proyecto_id)
            .first()
        )
