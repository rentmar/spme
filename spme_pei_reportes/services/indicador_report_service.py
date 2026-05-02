# services/indicador_report_service.py
from typing import Dict, Optional
from .base.base_report_service import BaseReportService
from ..repositories.indicador_repository import IndicadorRepository
from ..serializers.estructura_pei_serializer import EstructuraPEISerializer


class IndicadorReportService(BaseReportService):
    """Servicio para construir árbol de reporte desde un indicador."""
    
    def __init__(self):
        self.ind_repo = IndicadorRepository()
    
    def build_report_tree(
        self,
        elemento_id: int,
        profundidad: Optional[int] = None,
        **filtros
    ) -> Optional[Dict]:
        """Construye el árbol desde un indicador."""
        indicador = self.ind_repo.get_indicador_polimorfico(elemento_id)
        
        if not indicador:
            return None
        
        serializer = EstructuraPEISerializer(
            profundidad=profundidad if profundidad is not None else 0,
        )
        
        return serializer.serializar_indicador_individual(indicador)