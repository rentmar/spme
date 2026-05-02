#repositories/pei_repository.py
from typing import Optional, Dict
from django.db.models import Prefetch
from spme_estructuracion_pei.models import Pei, ObjetivoPei

class PEIRepository:
    """Repositorio para consultas optimizadas de PEI"""

    def get_pei_completo(self, pei_id: int) -> Optional[Pei]:
        """Obtiene PEI con todas sus relaciones precargadas"""
        try:
            return Pei.objects.prefetch_related(
                Prefetch(
                    'pei_obj_general',
                    queryset=ObjetivoPei.objects.prefetch_related(
                        'factores_criticos', 'indicador_pei_objetivo'
                    )
                )
            ).get(id=pei_id)
        except Pei.DoesNotExist:
            return None
    
    def get_pei_resumen(self, pei_id: int) -> Optional[Dict]:
        """Obtiene solo datos basicos del PEI con values()"""
        return Pei.objects.filter(id=pei_id).values(
            'id', 'titulo', 'descripcion', 'fecha_inicio',
            'fecha_fin', 'esta_vigente', 'fecha_creacion'
        ).first()