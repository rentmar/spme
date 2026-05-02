#repositories/indicador_repository.py
from typing import Optional
from django.db.models import QuerySet
from spme_estructuracion_pei.models import IndicadorPeiBase


class IndicadorRepository:
    """Repositorio para consultas polimórficas de indicadores."""
    
    def get_indicador_polimorfico(self, indicador_id: int) -> Optional[IndicadorPeiBase]:
        """Obtiene un indicador resolviendo su tipo polimórfico."""
        try:
            # Obtener el registro base
            base = IndicadorPeiBase.objects.select_related(
                'objetivo__pei'
            ).get(id=indicador_id)
            
            # En lugar de get_subclass(), retornamos el objeto base
            # Los atributos específicos (numerador, umbrales) se acceden
            # directamente porque django-polymorphic los hace disponibles
            return base
            
        except IndicadorPeiBase.DoesNotExist:
            return None
    
    def get_indicadores_by_objetivo(
        self,
        objetivo_id: int,
        tipo: str = None
    ) -> QuerySet:
        """Obtiene indicadores de un objetivo con filtro opcional por tipo."""
        queryset = IndicadorPeiBase.objects.filter(objetivo_id=objetivo_id)
        
        if tipo == 'CUANTITATIVO':
            queryset = queryset.filter(indicadorpeicuantitativo__isnull=False)
        elif tipo == 'CUALITATIVO':
            queryset = queryset.filter(indicadorpeicualitativo__isnull=False)
        
        return queryset.order_by('codigo') 