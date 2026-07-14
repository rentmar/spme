# spme/apptran/formularios/repositories/forma_pago_repository.py
from typing import List, Dict, Any
from django.apps import apps

class FormaPagoRepository:
    """
    Repositorio para acceder a los datos de forma de pago de los modelos
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
                # Log del error si el modelo no existe
                continue
        return modelos
    
    def obtener_registros_con_datos_pago(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los registros con datos_forma_pago de todos los modelos.
        
        Returns:
            Lista de diccionarios con los datos crudos de cada registro.
        """
        registros = []

        for nombre_modelo, modelo in self.modelos_map.items():
            try:
                registros_modelo = self._obtener_datos_modelo(modelo)
                registros.extend(registros_modelo)
            except Exception as e:
                # Log del error para debugging
                print(f"Error procesando modelo {nombre_modelo}: {str(e)}")
                continue
        
        return registros
    
    def _obtener_datos_modelo(self, modelo) -> List[Dict[str, Any]]:
        """
        Obtiene los datos crudos de un modelo específico.
        
        Args:
            modelo: Clase del modelo Django
            
        Returns:
            Lista de diccionarios con datos_forma_pago y forma_pago_id
        """
        resultados = []

        queryset = modelo.objects.filter(
            datos_forma_pago__isnull=False
        ).select_related('formaPago')

        for instancia in queryset:
            if instancia.datos_forma_pago:  # Verificación adicional
                resultados.append({
                    'datos_forma_pago': instancia.datos_forma_pago,
                    'forma_pago_id': instancia.formaPago_id,
                })
        
        return resultados