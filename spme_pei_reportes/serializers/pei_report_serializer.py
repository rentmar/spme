#serializers/pei_report_serializer.py
from typing import Dict
from spme_estructuracion_pei.models import Pei

class PEIReportSerializer:
    """Serializa un modelo PEI a diccionario"""
    def serialize(self, pei: Pei) -> Dict:
        return {
            "id": pei.id,
            "titulo": pei.titulo,
            "descripcion": pei.descripcion or '',
            "fecha_inicio": pei.fecha_inicio.isoformat() if pei.fecha_inicio else None,
            "fecha_fin": pei.fecha_fin.isoformat() if pei.fecha_fin else None,
            "esta_vigente": pei.esta_vigente,
            "fecha_creacion": pei.fecha_creacion.isoformat() if hasattr(pei, 'fecha_creacion') else None,
        }
    