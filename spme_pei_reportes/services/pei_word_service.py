from io import BytesIO
from typing import Dict
from .generators.base_document import BaseDocument
from .generators.pei_generator import PEIGenerator
from .generators.objetivo_generator import ObjetivoGenerator
from .generators.factor_generator import FactorGenerator
from .generators.indicador_base_generator import IndicadorBaseGenerator
from .generators.indicador_cuantitativo_generator import IndicadorCuantitativoGenerator
from .generators.indicador_cualitativo_generator import IndicadorCualitativoGenerator


class PEIWordService:
    """Orquestador de generación de documentos Word."""
    def __init__(self):
        self.generators = {
            'pei': PEIGenerator(),
            'objetivo': ObjetivoGenerator(),
            'factor_critico': FactorGenerator(),
            'indicador': IndicadorBaseGenerator(),
        }
        self.subtipo_generators = {
            'cuantitativo': IndicadorCuantitativoGenerator(),
            'cualitativo': IndicadorCualitativoGenerator(),
        } 

    def generate_document(self, arbol: Dict) -> BytesIO:
        self.base_doc = BaseDocument()
        self._process_node(arbol, nivel=0)
        return self.base_doc.save_to_bytes()

    def _process_node(self, nodo: Dict, nivel: int):
        tipo = nodo.get('tipo')
        if not tipo:
            return

        # DEBUG
        print(f"Procesando: tipo={tipo}, nivel={nivel}")

        subtipo = nodo.get('subtipo')
        if tipo == 'indicador' and subtipo:
            generator = self.subtipo_generators.get(subtipo)
        else:
            generator = self.generators.get(tipo)

        if generator:
            try:
                generator.generate(self.base_doc, nodo, nivel)
                print(f"  OK: {tipo}")
            except Exception as e:
                print(f"  ERROR en {tipo}: {e}")
                import traceback
                traceback.print_exc()

        for hijo in nodo.get('hijos', []):
            self._process_node(hijo, nivel + 1)

    def registrar_generador(self, tipo: str, generador) -> None:
        self.generators[tipo] = generador