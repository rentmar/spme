# spme_presupuesto/serializers/arbol_pres_plan_serializer.py

from rest_framework import serializers

class NodoPresPlanSerializer(serializers.Serializer):
    """
    Serializer para el nodo raíz del árbol de presupuesto planificado.
    
    Campos:
        - tipo_nodo: Identificador del tipo de nodo
        - id: ID del proyecto en la base de datos
        - nivel: Profundidad en el árbol (0 = raíz)
        - datos: Información específica del proyecto
        - actividades: Lista con contenedor de actividades y resumen
        - metadata: Información adicional del árbol
    """
    tipo_nodo = serializers.CharField(
        help_text="Tipo de nodo: proyecto"
    )
    id = serializers.IntegerField(
        help_text="ID del proyecto"
    )
    nivel = serializers.IntegerField(
        help_text="Nivel de profundidad (0 = raíz)"
    )
    datos = serializers.DictField(
        help_text="Datos del proyecto (código, título, presupuesto, etc.)"
    )
    actividades = serializers.ListField(
        child=serializers.DictField(),
        default=list,
        help_text="Contenedor de actividades + resumen del proyecto"
    )
    metadata = serializers.DictField(
        default=dict,
        help_text="Metadatos del árbol (total actividades, presupuesto, etc.)"
    )