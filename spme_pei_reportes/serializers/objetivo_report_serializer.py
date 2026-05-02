#serializers/objetivo_report_serializer.py
from typing import Dict
from spme_estructuracion_pei.models import ObjetivoPei


class ObjetivoReportSerializer:
    """Serializa un modelo ObjetivoPei a diccionario."""
    
    def serialize(self, objetivo: ObjetivoPei) -> Dict:
        return {
            "id": objetivo.id,
            "codigo": objetivo.codigo or '',
            "descripcion": objetivo.descripcion or '',
            "pei_id": objetivo.pei_id,
            "pei_titulo": objetivo.pei.titulo if objetivo.pei else '',
        }