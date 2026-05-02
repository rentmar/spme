#services/pei_report_service.py
from typing import Dict, Optional
from .base.base_report_service import BaseReportService
from ..repositories.pei_repository import PEIRepository
from ..serializers.estructura_pei_serializer import EstructuraPEISerializer 

class PEIReportService(BaseReportService):
    """Servicio para construir árbol de reporte desde un PEI."""
    def __init__(self):
        self.pei_repo = PEIRepository()
    
    def build_report_tree(self, elemento_id: int, profundidad: Optional[int] = None, **filtros) -> Optional[Dict]:
        pei = self.pei_repo.get_pei_completo(elemento_id)
        if not pei:
            return None
        serializer = EstructuraPEISerializer(
            profundidad=profundidad if profundidad is not None else 2,
            incluir_factores=filtros.get('incluir_factores', True),
            incluir_indicadores=filtros.get('incluir_indicadores', True),
            tipo_indicador=filtros.get('tipo_indicador', 'TODOS'),
        )
        return serializer.serializar_pei(pei)