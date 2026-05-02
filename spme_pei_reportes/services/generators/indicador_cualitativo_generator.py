# services/generators/indicador_cualitativo_generator.py
from .indicador_base_generator import IndicadorBaseGenerator

class IndicadorCualitativoGenerator(IndicadorBaseGenerator):
    
    def _obtener_campos_especificos(self, datos: dict) -> list:
        return [
            ('Umbral 1', datos.get('umbral_des_literal_um1', '')),
            ('Umbral 2', datos.get('umbral_des_literal_um2', '')),
            ('Umbral 3', datos.get('umbral_des_literal_um3', '')),
        ]