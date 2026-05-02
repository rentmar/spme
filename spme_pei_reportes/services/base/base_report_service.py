#services/base/base_report_service.py
from abc import ABC, abstractmethod
from typing import Dict, Optional 

class BaseReportService(ABC):
    """Clase base abstracta para servicios de reporte."""
    @abstractmethod
    def build_report_tree(self, elemento_id: int, profundidad: Optional[int] = None, **filtros) -> Optional[Dict]:
        pass