# services/forma_pago_service.py

from typing import Dict, List, Any
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class FormaPagoService:
    """Servicio para procesar y agrupar datos de forma de pago."""
    
    TIPO_EFECTIVO = 'efectivo'
    TIPO_TRANSFERENCIA = 'transferencia'
    TIPO_CHEQUE = 'cheque'
    
    FORMA_PAGO_EFECTIVO = 1
    FORMA_PAGO_TRANSFERENCIA = 2
    FORMA_PAGO_CHEQUE = 3
    
    def __init__(self, repository):
        self.repository = repository
    
    def obtener_beneficiarios_agrupados(self) -> Dict[str, List[Dict[str, Any]]]:
        """Obtiene, procesa y agrupa beneficiarios por tipo de forma de pago."""
        try:
            registros_crudos = self.repository.obtener_registros_con_datos_pago()
        except Exception as e:
            logger.error(f"Error obteniendo registros: {str(e)}")
            raise
            
        todos_registros = []
        
        for item in registros_crudos:
            try:
                datos = item['datos_forma_pago']
                forma_pago_id = item['forma_pago_id']
                
                if not datos or not forma_pago_id:
                    continue
                
                if self._es_formato_antiguo(datos):
                    registros = self._convertir_formato_antiguo(datos, forma_pago_id)
                elif self._es_formato_nuevo(datos):
                    registros = self._procesar_formato_nuevo(datos, forma_pago_id)
                else:
                    logger.warning(f"Formato de datos no reconocido: {datos}")
                    continue
                    
                todos_registros.extend(registros)
                
            except Exception as e:
                logger.error(f"Error procesando registro: {str(e)}")
                continue
        
        return self._procesar_y_agrupar(todos_registros)
    
    def _es_formato_antiguo(self, datos: Dict) -> bool:
        """Verifica formato antiguo: {otros: {...}, transferencia: {...}}"""
        return (
            isinstance(datos, dict) and
            'otros' in datos and
            'transferencia' in datos and
            'efectivo' not in datos and
            'cheque' not in datos
        )
    
    def _es_formato_nuevo(self, datos: Dict) -> bool:
        """Verifica formato nuevo: {efectivo, transferencia, cheque, otros}"""
        claves_requeridas = {'efectivo', 'transferencia', 'cheque', 'otros'}
        return (
            isinstance(datos, dict) and
            claves_requeridas.issubset(datos.keys())
        )
    
    def _convertir_formato_antiguo(self, datos: Dict, forma_pago_id: int) -> List[Dict]:
        """Convierte formato antiguo al nuevo."""
        registros = []
        
        if forma_pago_id == self.FORMA_PAGO_EFECTIVO:
            otros = datos.get('otros', {})
            if otros.get('ci_otros'):
                registros.append({
                    'tipo': self.TIPO_EFECTIVO,
                    'ci': otros['ci_otros'],
                    'nombre': otros.get('nombre_otros', ''),
                })
                
        elif forma_pago_id == self.FORMA_PAGO_TRANSFERENCIA:
            transferencia = datos.get('transferencia', {})
            if transferencia.get('ci_transferencia'):
                registros.append({
                    'tipo': self.TIPO_TRANSFERENCIA,
                    'ci': transferencia.get('ci_transferencia', ''),
                    'nombre': transferencia.get('nombre_transferencia', ''),
                    'banco': transferencia.get('entidad_bancaria', ''),
                    'tipo_cuenta': transferencia.get('tipo_cuenta', ''),
                    'numero_cuenta': transferencia.get('numero_cuenta', ''),
                })
                
        elif forma_pago_id == self.FORMA_PAGO_CHEQUE:
            otros = datos.get('otros', {})
            if otros.get('ci_otros'):
                registros.append({
                    'tipo': self.TIPO_CHEQUE,
                    'ci': otros['ci_otros'],
                    'nombre': otros.get('nombre_otros', ''),
                })
        
        return registros
    
    def _procesar_formato_nuevo(self, datos: Dict, forma_pago_id: int) -> List[Dict]:
        """Procesa el formato nuevo."""
        registros = []
        
        # Efectivo
        efectivo = datos.get('efectivo', {})
        if efectivo.get('ci_efectivo'):
            registros.append({
                'tipo': self.TIPO_EFECTIVO,
                'ci': efectivo['ci_efectivo'],
                'nombre': efectivo.get('nombre_efectivo', ''),
            })
        
        # Transferencia
        transferencia = datos.get('transferencia', {})
        if transferencia.get('ci_transferencia'):
            registros.append({
                'tipo': self.TIPO_TRANSFERENCIA,
                'ci': transferencia.get('ci_transferencia', ''),
                'nombre': transferencia.get('nombre_transferencia', ''),
                'banco': transferencia.get('entidad_bancaria', ''),
                'tipo_cuenta': transferencia.get('tipo_cuenta', ''),
                'numero_cuenta': transferencia.get('numero_cuenta', ''),
            })
        
        # Cheque
        cheque = datos.get('cheque', {})
        if cheque.get('ci_cheque'):
            registros.append({
                'tipo': self.TIPO_CHEQUE,
                'ci': cheque['ci_cheque'],
                'nombre': cheque.get('nombre_cheque', ''),
            })
        
        return registros
    
    def _contar_campos_con_datos(self, registro: Dict) -> int:
        """Cuenta cuántos campos tienen datos (no vacíos)."""
        count = 0
        for key, value in registro.items():
            if key not in ('tipo',) and value:
                count += 1
        return count
    
    def _procesar_y_agrupar(self, registros: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Agrupa por tipo, elimina duplicados por CI.
        Criterio: permanece el registro con más datos.
        En caso de empate, permanece el de transferencia.
        """
        ci_map = {}
        
        for registro in registros:
            ci = registro['ci']
            
            if ci not in ci_map:
                ci_map[ci] = registro
            else:
                actual = ci_map[ci]
                campos_actual = self._contar_campos_con_datos(actual)
                campos_nuevo = self._contar_campos_con_datos(registro)
                
                if campos_nuevo > campos_actual:
                    ci_map[ci] = registro
                elif campos_nuevo == campos_actual:
                    if registro['tipo'] == self.TIPO_TRANSFERENCIA and actual['tipo'] != self.TIPO_TRANSFERENCIA:
                        ci_map[ci] = registro
        
        agrupados = defaultdict(list)
        for registro in ci_map.values():
            tipo = registro.pop('tipo')
            agrupados[tipo].append(registro)
        
        todos = [{k: v for k, v in reg.items()} for reg in ci_map.values()]
        
        return {
            self.TIPO_EFECTIVO: agrupados.get(self.TIPO_EFECTIVO, []),
            self.TIPO_TRANSFERENCIA: agrupados.get(self.TIPO_TRANSFERENCIA, []),
            self.TIPO_CHEQUE: agrupados.get(self.TIPO_CHEQUE, []),
            'todos': todos,
        }