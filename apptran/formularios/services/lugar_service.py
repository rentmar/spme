# spme/apptran/formularios/services/lugar_service.py
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class LugarService:
    """Servicio para procesar y agrupar lugares de solicitud."""
    
    def __init__(self, repository):
        self.repository = repository
    
    def obtener_lugares_agrupados(self) -> Dict[str, Any]:
        """
        Obtiene, procesa y agrupa lugares de todos los formularios.
        
        Returns:
            Diccionario con:
            - lugares_unicos: Lista de lugares únicos ordenados alfabéticamente
            - lugares_por_tipo: Lugares agrupados por tipo de formulario
            - total_registros: Total de registros procesados
        """
        try:
            registros_lugares = self.repository.obtener_lugares()
        except Exception as e:
            logger.error(f"Error obteniendo lugares: {str(e)}")
            raise
        
        # Extraer y normalizar lugares
        lugares_unicos = set()
        lugares_por_tipo = {}
        contador_por_lugar = {}
        detalles_por_lugar = {}
        
        for registro in registros_lugares:
            lugar = self._normalizar_lugar(registro['lugar'])
            tipo = registro['tipo_formulario']
            
            if not lugar:
                continue
            
            # Agregar a lugares únicos
            lugares_unicos.add(lugar)
            
            # Contar ocurrencias por lugar
            contador_por_lugar[lugar] = contador_por_lugar.get(lugar, 0) + 1
            
            # Agrupar por tipo de formulario
            if tipo not in lugares_por_tipo:
                lugares_por_tipo[tipo] = set()
            lugares_por_tipo[tipo].add(lugar)
            
            # Guardar detalles del registro
            if lugar not in detalles_por_lugar:
                detalles_por_lugar[lugar] = []
            detalles_por_lugar[lugar].append({
                'formulario_id': registro['formulario_id'],
                'numero_formulario': registro['numero_formulario'],
                'tipo_formulario': self._get_nombre_legible(tipo),
            })
        
        # Ordenar lugares alfabéticamente
        lugares_ordenados = sorted(list(lugares_unicos))
        
        # Convertir sets a listas ordenadas en lugares_por_tipo
        lugares_por_tipo_ordenados = {
            self._get_nombre_legible(tipo): sorted(list(lugares))
            for tipo, lugares in lugares_por_tipo.items()
        }
        
        # Crear lista de lugares con estadísticas
        lugares_con_stats = [
            {
                'nombre': lugar,
                'cantidad_registros': contador_por_lugar.get(lugar, 0),
                'tipos_formulario': list(set(
                    self._get_nombre_legible(d['tipo_formulario'])
                    for d in detalles_por_lugar.get(lugar, [])
                )),
            }
            for lugar in lugares_ordenados
        ]
        
        return {
            'lugares_unicos': lugares_ordenados,
            'lugares_por_tipo': lugares_por_tipo_ordenados,
            'lugares_con_estadisticas': lugares_con_stats,
            'total_lugares_unicos': len(lugares_ordenados),
            'total_registros': len(registros_lugares),
        }
    
    def _normalizar_lugar(self, lugar: str) -> str:
        """
        Normaliza el nombre del lugar:
        - Elimina espacios extras
        - Capitaliza primeras letras
        """
        if not lugar:
            return ''
        
        # Eliminar espacios múltiples y strip
        lugar = ' '.join(lugar.split())
        
        # Capitalizar cada palabra (excepto artículos y preposiciones)
        # Para nombres propios, mejor mantener como están
        return lugar.strip()
    
    def _get_nombre_legible(self, tipo_modelo: str) -> str:
        """Convierte el nombre del modelo a un formato legible."""
        mapping = {
            'SolicitudFondos': 'Solicitud de Fondos',
            'SolicitudViaje': 'Solicitud de Viaje',
            'SolicitudPagoDirecto': 'Solicitud de Pago Directo',
            'SolicitudReembolso': 'Solicitud de Reembolso',
        }
        return mapping.get(tipo_modelo, tipo_modelo)