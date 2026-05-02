# services/objetivo_report_service.py
from typing import Dict, Optional
from .base.base_report_service import BaseReportService
from ..repositories.objetivo_repository import ObjetivoRepository
from ..serializers.estructura_pei_serializer import EstructuraPEISerializer


class ObjetivoReportService(BaseReportService):
    """Servicio para construir árbol de reporte desde un objetivo."""
    
    def __init__(self):
        self.obj_repo = ObjetivoRepository()
    
    def build_report_tree(
        self,
        elemento_id: int,
        profundidad: Optional[int] = None,
        **filtros
    ) -> Optional[Dict]:
        """Construye el árbol desde un objetivo."""
        objetivo = self.obj_repo.get_objetivo_con_relaciones(
            elemento_id,
            incluir_factores=filtros.get('incluir_factores', True),
            incluir_indicadores=filtros.get('incluir_indicadores', True),
        )
        
        if not objetivo:
            return None
        
        serializer = EstructuraPEISerializer(
            profundidad=profundidad if profundidad is not None else 2,
            incluir_factores=filtros.get('incluir_factores', True),
            incluir_indicadores=filtros.get('incluir_indicadores', True),
        )
        
        return serializer.serializar_objetivo_individual(objetivo)