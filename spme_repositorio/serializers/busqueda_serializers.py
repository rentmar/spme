"""
Serializadores para el buscador global.
"""

from rest_framework import serializers


class ProyectoBusquedaSerializer(serializers.Serializer):
    """Serializador para información de proyecto en resultados de búsqueda."""
    id = serializers.IntegerField(allow_null=True)
    nombre = serializers.CharField(allow_null=True)
    codigo = serializers.CharField(allow_null=True, allow_blank=True)


class NodoBusquedaSerializer(serializers.Serializer):
    """Serializador para información del nodo en resultados de búsqueda."""
    id = serializers.IntegerField(allow_null=True)
    tipo = serializers.CharField(allow_null=True)
    nombre = serializers.CharField(allow_null=True)
    codigo = serializers.CharField(allow_null=True, allow_blank=True)


class ResultadoBusquedaSerializer(serializers.Serializer):
    """Serializador para resultados individuales de búsqueda."""
    id = serializers.IntegerField()
    tipo_resultado = serializers.CharField()
    nombre = serializers.CharField()
    fecha_creacion = serializers.DateTimeField()
    proyecto = ProyectoBusquedaSerializer(allow_null=True)
    nodo = NodoBusquedaSerializer(allow_null=True)
    
    # Campos de adjunto - TODOS opcionales
    tipo_archivo = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    mime_type = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    tamano = serializers.IntegerField(required=False, allow_null=True)
    descripcion = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    archivo_id = serializers.IntegerField(required=False, allow_null=True)
    adjunto_id = serializers.IntegerField(required=False, allow_null=True)
    
    # Campos de referencia - TODOS opcionales
    categoria = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    url = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    referencia_id = serializers.IntegerField(required=False, allow_null=True)


class BusquedaResponseSerializer(serializers.Serializer):
    """Serializador para la respuesta completa de búsqueda."""
    total = serializers.IntegerField()
    pagina = serializers.IntegerField()
    por_pagina = serializers.IntegerField()
    total_paginas = serializers.IntegerField()
    tipo = serializers.CharField()
    resultados = ResultadoBusquedaSerializer(many=True)