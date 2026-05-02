# serializers/estructura_pei_serializer.py
from typing import Dict
from spme_estructuracion_pei.models import (
    Pei,
    ObjetivoPei,
    FactoresCriticos,
    IndicadorPeiBase
)
from .pei_report_serializer import PEIReportSerializer
from .objetivo_report_serializer import ObjetivoReportSerializer
from .factor_report_serializer import FactorReportSerializer
from .indicador_report_serializer import IndicadorReportSerializer

class EstructuraPEISerializer:
    """
    Constructor del Arbol Jerarquico del PEI
    NIVELES:
    0: Solo PEI
    1: +Objetivos
    2: +Factores/Indicadores
    """
    
    def __init__(self, profundidad: int = 2, **opciones):
        self.profundidad = profundidad if profundidad is not None else 2
        self.incluir_factores = opciones.get('incluir_factores', True)
        self.incluir_indicadores = opciones.get('incluir_indicadores', True)
        self.tipo_indicador = opciones.get('tipo_indicador', 'TODOS')

        self.pei_serializer = PEIReportSerializer()
        self.obj_serializer = ObjetivoReportSerializer()
        self.fac_serializer = FactorReportSerializer()
        self.ind_serializer = IndicadorReportSerializer()
    
    def serializar_pei(self, pei: Pei) -> Dict:
        """Construye el arbol completo desde un PEI"""
        nodo = {
            "tipo": "pei", 
            "nivel": 0, 
            "datos": self.pei_serializer.serialize(pei), "hijos": []
            }
        
        if self.profundidad >= 1:
            for objetivo in pei.pei_obj_general.all():
                nodo["hijos"].append(self._serializar_objetivo(objetivo))
        return nodo
    
    def serializar_objetivo_individual(self, objetivo: ObjetivoPei) -> Dict:
        """Construye Arbol desde un objetivo"""
        return self._serializar_objetivo(objetivo)
    
    def _serializar_objetivo(self, objetivo: ObjetivoPei) -> Dict:
        """Serializa un objetivo y sus hijos."""
        nodo = {
            "tipo": "objetivo", 
            "nivel": 1, 
            "datos": self.obj_serializer.serialize(objetivo), 
            "hijos": []
            }
        
        if self.profundidad >= 2:
            if self.incluir_factores:
                for factor in objetivo.factores_criticos.all():
                    nodo["hijos"].append({
                        "tipo": "factor_critico", "nivel": 2,
                        "datos": self.fac_serializer.serialize(factor), "hijos": []
                    })
            if self.incluir_indicadores:
                for indicador in objetivo.indicador_pei_objetivo.all():
                    datos_ind = self.ind_serializer.serialize(indicador)
                    nodo["hijos"].append({
                        "tipo": "indicador",
                        "subtipo": datos_ind.get('subtipo', ''),
                        "nivel": 2,
                        "datos": datos_ind,
                        "hijos": []
                    })
        return nodo
    
    def serializar_factor_individual(self, factor: FactoresCriticos) -> Dict:
        """Construye árbol desde un factor crítico."""
        nodo = {"tipo": "factor_critico", "nivel": 0, "datos": self.fac_serializer.serialize(factor), "hijos": []}
        if self.profundidad >= 1 and factor.objetivo_especifico:
            nodo["hijos"].append({
                "tipo": "objetivo", "nivel": 1,
                "datos": self.obj_serializer.serialize(factor.objetivo_especifico), "hijos": []
            })
        return nodo
    
    def serializar_indicador_individual(self, indicador: IndicadorPeiBase) -> Dict:
        """Construye árbol desde un indicador."""
        datos_ind = self.ind_serializer.serialize(indicador)
        nodo = {
            "tipo": "indicador",
            "subtipo": datos_ind.get('subtipo', ''),
            "nivel": 0,
            "datos": datos_ind,
            "hijos": []
        }
        if self.profundidad >= 1 and indicador.objetivo:
            nodo["hijos"].append({
                "tipo": "objetivo", "nivel": 1,
                "datos": self.obj_serializer.serialize(indicador.objetivo), "hijos": []
            })
        return nodo