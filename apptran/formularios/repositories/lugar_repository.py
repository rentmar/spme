# spme/apptran/formularios/repositories/lugar_repository.py
from typing import List, Dict, Any
from django.apps import apps
import logging

logger = logging.getLogger(__name__)

class LugarRepository:
    """
    Repositorio para acceder a los lugares de solicitud de los modelos
    """
    MODELOS = [
        'SolicitudFondos',
        'SolicitudViaje',
        'SolicitudPagoDirecto',
        'SolicitudReembolso',
    ]

    def __init__(self):
        self.modelos_map = self._get_modelos_map()
    
    def _get_modelos_map(self):
        """Obtiene los modelos registrados."""
        modelos = {}
        for nombre in self.MODELOS:
            try:
                modelos[nombre] = apps.get_model('spme_monitoreo', nombre)
            except LookupError:
                logger.warning(f"Modelo {nombre} no encontrado")
                continue
        return modelos
    
    def obtener_lugares(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los lugares de solicitud de todos los modelos.
        
        Returns:
            Lista de diccionarios con el lugar y metadatos del registro.
        """
        lugares = []

        for nombre_modelo, modelo in self.modelos_map.items():
            try:
                lugares_modelo = self._obtener_lugares_modelo(modelo, nombre_modelo)
                lugares.extend(lugares_modelo)
            except Exception as e:
                logger.error(f"Error procesando modelo {nombre_modelo}: {str(e)}")
                continue
        
        return lugares
    
    def _obtener_lugares_modelo(self, modelo, nombre_modelo: str) -> List[Dict[str, Any]]:
        """
        Obtiene los lugares de un modelo específico.
        
        Args:
            modelo: Clase del modelo Django
            nombre_modelo: Nombre del modelo para referencia
            
        Returns:
            Lista de diccionarios con lugar y tipo de formulario
        """
        resultados = []

        queryset = modelo.objects.filter(
            lugarSolicitud__isnull=False
        ).exclude(
            lugarSolicitud=''
        ).values('id', 'lugarSolicitud', 'numeroFormulario')

        for item in queryset:
            lugar = item['lugarSolicitud'].strip()
            if lugar:  # Verificar que no esté vacío después de strip
                resultados.append({
                    'lugar': lugar,
                    'formulario_id': item['id'],
                    'numero_formulario': item.get('numeroFormulario', ''),
                    'tipo_formulario': nombre_modelo,
                })
        
        return resultados