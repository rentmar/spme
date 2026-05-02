# repositories/objetivo_repository.py
from typing import Optional
from django.db.models import QuerySet
from spme_estructuracion_pei.models import ObjetivoPei

class ObjetivoRepository:
    """Repositorio para consultas de objetivos del PEI."""
    def get_objetivo_con_relaciones(self, objetivo_id: int, incluir_factores: bool = True, incluir_indicadores: bool = True) -> Optional[ObjetivoPei]:
        queryset = ObjetivoPei.objects.select_related('pei')
        if incluir_factores and incluir_indicadores:
            queryset = queryset.prefetch_related('factores_criticos', 'indicador_pei_objetivo')
        elif incluir_factores:
            queryset = queryset.prefetch_related('factores_criticos')
        elif incluir_indicadores:
            queryset = queryset.prefetch_related('indicador_pei_objetivo')
        try:
            return queryset.get(id=objetivo_id)
        except ObjetivoPei.DoesNotExist:
            return None
    
    def get_objetivos_by_pei(self, pei_id: int) -> QuerySet:
        return ObjetivoPei.objects.filter(pei_id=pei_id).order_by('codigo')


