# spme/spme_tree_reporter/serializers/generar_reporte_serializer.py
"""
Serializer para validar los parámetros del endpoint de generación de reportes.
"""

from rest_framework import serializers


class GenerarReporteSerializer(serializers.Serializer):
    """
    Valida los parámetros de entrada para generar un reporte.
    
    Parámetros aceptados:
        nodo: Tipo de nodo inicial
        id: ID del nodo
        profundidad: Niveles a incluir
        tipo: Configuración predefinida
        modo_actividades: Cómo tratar actividades transversales
        incluir_portada: Si generar portada
        incluir_indice: Si generar índice
    """
    
    # === OPCIONES VÁLIDAS ===
    
    PROFUNDIDAD_CHOICES = ['self', '1', '2', '3', '4', 'all']
    TIPO_REPORTE_CHOICES = ['completo', 'ejecutivo', 'gerencial', 'operativo', 'ficha_tecnica', 'personalizado']
    MODO_ACTIVIDADES_CHOICES = ['omitir', 'referencia', 'anexo']
    
    # === CAMPOS ===
    
    nodo = serializers.CharField(
        default='proyecto',
        max_length=50,
        help_text="Tipo de nodo inicial. Ej: 'proyecto', 'objetivogeneral', 'actividad'"
    )
    
    id = serializers.IntegerField(
        required=True,
        help_text="ID del nodo"
    )
    
    profundidad = serializers.CharField(
        default='all',
        help_text="Niveles a incluir: 'self', '1', '2', '3', '4', 'all'"
    )
    
    tipo = serializers.CharField(
        default='completo',
        help_text="Tipo de reporte predefinido: 'completo', 'ejecutivo', 'gerencial', 'operativo', 'ficha_tecnica', 'personalizado'"
    )
    
    modo_actividades = serializers.ChoiceField(
        choices=MODO_ACTIVIDADES_CHOICES,
        default='anexo',
        help_text="Cómo tratar actividades: 'omitir', 'referencia', 'anexo'"
    )
    
    incluir_portada = serializers.BooleanField(
        default=True,
        help_text="Incluir portada (solo aplica si nodo='proyecto')"
    )
    
    incluir_indice = serializers.BooleanField(
        default=True,
        help_text="Incluir índice de contenidos (solo aplica si nodo='proyecto')"
    )
    
    # === VALIDACIONES DE CAMPO ===
    
    def validate_nodo(self, value):
        """Valida que el tipo de nodo esté registrado en el RendererRegistry."""
        from ..services.renderers import RendererRegistry
        
        registry = RendererRegistry()
        tipos_validos = registry.get_registered_types()
        
        if value not in tipos_validos:
            raise serializers.ValidationError(
                f"Tipo de nodo '{value}' no soportado. "
                f"Tipos válidos: {', '.join(sorted(tipos_validos))}"
            )
        
        return value
    
    def validate_profundidad(self, value):
        """Valida que la profundidad sea un valor aceptado."""
        if value not in self.PROFUNDIDAD_CHOICES:
            raise serializers.ValidationError(
                f"Profundidad '{value}' no válida. Usar: {self.PROFUNDIDAD_CHOICES}"
            )
        return value
    
    def validate_tipo(self, value):
        """Valida que el tipo de reporte sea válido."""
        if value not in self.TIPO_REPORTE_CHOICES:
            raise serializers.ValidationError(
                f"Tipo de reporte '{value}' no válido. Usar: {self.TIPO_REPORTE_CHOICES}"
            )
        return value
    
    # === VALIDACIONES CRUZADAS ===
    
    def validate(self, data):
        """
        Validaciones que dependen de múltiples campos.
        """
        nodo = data.get('nodo', 'proyecto')
        tipo = data.get('tipo', 'completo')
        
        # La portada y el índice solo aplican para reportes de proyecto
        if nodo != 'proyecto':
            data['incluir_portada'] = False
            data['incluir_indice'] = False
        
        # Si el tipo es predefinido (no 'personalizado'), limpiar overrides
        if tipo != 'personalizado':
            data.pop('profundidad', None)
            data.pop('modo_actividades', None)
        
        return data
    
    # === MÉTODO PARA OBTENER CONFIGURACIÓN LIMPIA ===
    
    def get_config(self) -> dict:
        """
        Retorna un diccionario limpio con la configuración validada.
        Listo para pasar al ReporteProyectoService.
        """
        data = self.validated_data
        
        return {
            'tipo_nodo': data.get('nodo', 'proyecto'),
            'nodo_id': data.get('id'),
            'profundidad': data.get('profundidad', 'all'),
            'tipo': data.get('tipo', 'completo'),
            'modo_actividades': data.get('modo_actividades', 'anexo'),
            'incluir_portada': data.get('incluir_portada', True),
            'incluir_indice': data.get('incluir_indice', True),
        }