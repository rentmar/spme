#services/factor_report_service.py
from typing import Dict, Optional
from .base.base_report_service import BaseReportService
from ..repositories.factor_repository import FactorRepository
from ..serializers.estructura_pei_serializer import EstructuraPEISerializer


class FactorReportService(BaseReportService):
    """Servicio para construir árbol de reporte desde un factor crítico."""
    
    def __init__(self):
        self.factor_repo = FactorRepository()
    
    def build_report_tree(
        self,
        elemento_id: int,
        profundidad: Optional[int] = None,
        **filtros
    ) -> Optional[Dict]:
        """Construye el árbol desde un factor crítico."""
        factor = self.factor_repo.get_factor_con_objetivo(elemento_id)
        
        if not factor:
            return None
        
        serializer = EstructuraPEISerializer(
            profundidad=profundidad if profundidad is not None else 1,
        )
        
        return serializer.serializar_factor_individual(factor)