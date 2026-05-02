#serializers/indicador_report_serializer.py
from typing import Dict
from spme_estructuracion_pei.models import (
    IndicadorPeiBase,
    IndicadorPeiCualitativo,
    IndicadorPeiCuantitativo,
)

from .indicador_cuantitativo_serializer import IndicadorCuantitativoSerializer
from .indicador_cualitativo_serializer import IndicadorCualitativoSerializer

class IndicadorReportSerializer:
    def __init__(self):
        self.serializadores = {
            'CUANTITATIVO': IndicadorCuantitativoSerializer(),
            'CUALITATIVO': IndicadorCualitativoSerializer(),
        }

    def serialize(self, indicador: IndicadorPeiBase) -> Dict:
        tipo = self._resolver_tipo(indicador)
        serializador = self.serializadores.get(tipo, self.serializadores['CUANTITATIVO'])
        datos = serializador.serialize(indicador)
        datos['tipo'] = 'indicador'
        datos['subtipo'] = tipo.lower()
        return datos

    def _resolver_tipo(self, indicador: IndicadorPeiBase) -> str:
        if isinstance(indicador, IndicadorPeiCuantitativo): return 'CUANTITATIVO'
        if isinstance(indicador, IndicadorPeiCualitativo): return 'CUALITATIVO'
        if hasattr(indicador, 'tipo'): return indicador.tipo
        return 'CUANTITATIVO'    




