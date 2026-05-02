# repositories/factor_repository.py
from typing import Optional
from django.db.models import QuerySet
from spme_estructuracion_pei.models import FactoresCriticos


class FactorRepository:
    """Repositorio para consultas de factores críticos."""
    
    def get_factor_con_objetivo(self, factor_id: int) -> Optional[FactoresCriticos]:
        """Obtiene un factor crítico con su objetivo padre."""
        try:
            return FactoresCriticos.objects.select_related(
                'objetivo_especifico__pei'
            ).get(id=factor_id)
        except FactoresCriticos.DoesNotExist:
            return None
    
    def get_factores_by_objetivo(self, objetivo_id: int) -> QuerySet:
        """Obtiene todos los factores de un objetivo."""
        return FactoresCriticos.objects.filter(
            objetivo_especifico_id=objetivo_id
        ).order_by('id')