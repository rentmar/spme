#serializers/factor_report_serializer.py
from typing import Dict
from spme_estructuracion_pei.models import FactoresCriticos

class FactorReportSerializer:
    """Serializa un modelo FactoresCriticos a diccionario."""
    
    def serialize(self, factor: FactoresCriticos) -> Dict:
        return {
            "id": factor.id,
            "factor_critico": factor.factor_critico or '',
            "objetivo_id": factor.objetivo_especifico_id,
            "objetivo_codigo": (
                factor.objetivo_especifico.codigo
                if factor.objetivo_especifico
                else ''
            ),
        }
