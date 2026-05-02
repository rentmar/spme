#serializers/indicador_cuantitativo_serializer.py
from typing import Dict
from spme_estructuracion_pei.models import IndicadorPeiCuantitativo

class IndicadorCuantitativoSerializer:
    """Serializa un IndicadorPeiCuantitativo a diccionario."""
    
    def serialize(self, indicador: IndicadorPeiCuantitativo) -> Dict:
        return {
            "id": indicador.id,
            "codigo": indicador.codigo or '',
            "descripcion": indicador.descripcion or '',
            "captura_informacion": indicador.captura_informacion or '',
            "responsabilidad": indicador.responsabilidad or '',
            "frecuencia_recopilacion": indicador.frecuencia_recopilacion or '',
            "uso_informacion": indicador.uso_informacion or '',
            "objetivo_id": indicador.objetivo_id,
            "objetivo_codigo": indicador.objetivo.codigo if indicador.objetivo else '',
            "tipo_medicion": "CUANTITATIVO",
            "numerador": indicador.numerador or '',
            "denominador": indicador.denominador or '',
            "umbral_des_numeral": indicador.umbral_des_numeral,
            "umbral_des_literal_um1": indicador.umbral_des_literal_um1 or '',
            "umbral_des_literal_um2": indicador.umbral_des_literal_um2 or '',
            "umbral_des_literal_um3": indicador.umbral_des_literal_um3 or '',
        }