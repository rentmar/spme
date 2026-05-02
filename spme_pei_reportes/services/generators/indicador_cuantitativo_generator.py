# services/generators/indicador_cuantitativo_generator.py
from .indicador_base_generator import IndicadorBaseGenerator

class IndicadorCuantitativoGenerator(IndicadorBaseGenerator):
    
    def _obtener_campos_especificos(self, datos: dict) -> list:
        return [
            ('Numerador', datos.get('numerador', '')),
            ('Denominador', datos.get('denominador', '')),
            ('Umbral Numeral', str(datos.get('umbral_des_numeral') or '')),
            ('Umbral Literal 1', datos.get('umbral_des_literal_um1', '')),
            ('Umbral Literal 2', datos.get('umbral_des_literal_um2', '')),
            ('Umbral Literal 3', datos.get('umbral_des_literal_um3', '')),
        ]