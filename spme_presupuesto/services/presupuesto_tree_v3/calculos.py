# spme/spme_presupuesto/services/presupuesto_tree_v3/calculos.py
from typing import List, Dict, Any
from decimal import Decimal


class CalculosPresupuestariosV3:
    """
    Cálculos presupuestarios para V3.
    """
    
    # Tipos de formulario que cuentan para ejecutado
    TIPOS_EJECUTABLES = {
        'rendicion_cuentas',
        'solicitud_reembolso',
    }
    
    # Estados que cuentan para ejecutado
    ESTADOS_EJECUTABLES = {'aprobado'}
    
    @classmethod
    def es_formulario_ejecutable(cls, formulario: Dict[str, Any]) -> bool:
        """
        Determina si un formulario cuenta para el ejecutado.
        
        Regla de negocio:
        - Solo Rendición de Cuentas y Solicitud de Reembolso
        - Solo estado aprobado
        """
        tipo = formulario.get('tipo', '')
        estado = formulario.get('estado', '')
        
        return (
            tipo in cls.TIPOS_EJECUTABLES and
            estado in cls.ESTADOS_EJECUTABLES
        )
    
    @classmethod
    def calcular_ejecutado_formularios(
        cls,
        formularios: List[Dict[str, Any]],
    ) -> float:
        """
        Calcula el ejecutado sumando formularios ejecutables.
        """
        total = 0.0
        
        for formulario in formularios:
            if cls.es_formulario_ejecutable(formulario):
                total += float(formulario.get('monto', 0))
        
        return total
    
    @classmethod
    def calcular_porcentaje(cls, ejecutado: float, planificado: float) -> float:
        """
        Calcula el porcentaje de ejecución.
        """
        if planificado <= 0:
            return 0.0
        
        return round((ejecutado / planificado) * 100, 2)
    
    @classmethod
    def consolidar_por_financiador(
        cls,
        desgloses: List[List[Dict[str, Any]]],
    ) -> List[Dict[str, Any]]:
        """
        Consolida desgloses por financiador.
        
        Args:
            desgloses: Lista de desgloses de financiadores.
        
        Returns:
            Lista consolidada de financiadores.
        """
        consolidado: Dict[str, Dict[str, Any]] = {}
        
        for desglose in desgloses:
            for financiador in desglose:
                nombre = financiador.get('nombre', '')
                monto = float(financiador.get('monto', 0))
                
                if nombre not in consolidado:
                    consolidado[nombre] = {
                        'nombre': nombre,
                        'monto': 0.0,
                    }
                    # Copiar sigla si existe
                    if 'sigla' in financiador:
                        consolidado[nombre]['sigla'] = financiador['sigla']
                
                consolidado[nombre]['monto'] += monto
        
        return list(consolidado.values())
    
    @classmethod
    def consolidar_formularios(
        cls,
        formularios_list: List[List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """
        Consolida formularios de múltiples nodos.
        
        Returns:
            Diccionario con totales y desglose por tipo.
        """
        total = {
            'cantidad': 0,
            'por_estado': {
                'aprobado': 0,
                'pendiente': 0,
                'rechazado': 0,
                'borrador': 0,
            },
        }
        
        por_tipo: Dict[str, Dict[str, Any]] = {}
        ejecutables = {
            'cantidad': 0,
            'monto_aprobado': 0.0,
            'por_tipo': {},
        }
        
        for formularios in formularios_list:
            for formulario in formularios:
                # Total
                total['cantidad'] += 1
                estado = formulario.get('estado', 'borrador')
                if estado in total['por_estado']:
                    total['por_estado'][estado] += 1
                
                # Por tipo
                tipo = formulario.get('tipo', 'desconocido')
                if tipo not in por_tipo:
                    por_tipo[tipo] = {
                        'cantidad': 0,
                        'monto_total': 0.0,
                    }
                por_tipo[tipo]['cantidad'] += 1
                por_tipo[tipo]['monto_total'] += float(formulario.get('monto', 0))
                
                # Ejecutables
                if cls.es_formulario_ejecutable(formulario):
                    ejecutables['cantidad'] += 1
                    ejecutables['monto_aprobado'] += float(formulario.get('monto', 0))
                    
                    if tipo not in ejecutables['por_tipo']:
                        ejecutables['por_tipo'][tipo] = {
                            'cantidad': 0,
                            'monto': 0.0,
                        }
                    ejecutables['por_tipo'][tipo]['cantidad'] += 1
                    ejecutables['por_tipo'][tipo]['monto'] += float(formulario.get('monto', 0))
        
        return {
            'total': total,
            'por_tipo': por_tipo,
            'ejecutables': ejecutables,
        }