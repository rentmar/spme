#services/composer/chain_composer.py
from typing import Dict
from ...utils.exceptions import ElementoNoEncontradoError, TipoElementoNoSoportadoError
from ...utils.utils import normalizar_profundidad
from ..base.base_report_service import BaseReportService
from ..pei_report_service import PEIReportService
from ..objetivo_report_service import ObjetivoReportService
from ..factor_report_service import FactorReportService
from ..indicador_report_service import IndicadorReportService

class ChainComposer:
    """
    Orquestador central. Servicios se registran progresivamente:
    HITO 1: 'pei', HITO 4: 'objetivo', HITO 5: 'factor', HITO 6: 'indicador'
    """
    def __init__(self):
        self._servicios: Dict[str, BaseReportService] = {}
        #self._servicios['pei'] = PEIReportService()
        self._init_servicios_default()

    #Servicios
    def _init_servicios_default(self):
        self._servicios = {
            'pei': PEIReportService(),
            'objetivo': ObjetivoReportService(),
            'factor': FactorReportService(),
            'indicador': IndicadorReportService(),
        }

    #Componer los reportes
    def compose(self, tipo_elemento: str, elemento_id: int, profundidad=None, **filtros) -> Dict:
        servicio = self._servicios.get(tipo_elemento)
        if not servicio:
            raise TipoElementoNoSoportadoError(tipo_elemento, list(self._servicios.keys()))
        try:
            profundidad = normalizar_profundidad(profundidad)
        except ValueError:
            from ...utils.exceptions import ProfundidadInvalidaError
            raise ProfundidadInvalidaError(str(profundidad))
        arbol = servicio.build_report_tree(elemento_id=elemento_id, profundidad=profundidad, **filtros)
        if not arbol:
            raise ElementoNoEncontradoError(tipo_elemento, elemento_id)
        return arbol
    
    def registrar_servicio(self, tipo: str, servicio: BaseReportService) -> None:
        """Registrar servicios"""
        self._servicios[tipo] = servicio