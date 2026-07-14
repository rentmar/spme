# spme/apptran/formularios/serializers/lugar_serializer.py
from rest_framework import serializers


class LugarEstadisticaSerializer(serializers.Serializer):
    """Serializer para lugares con estadísticas."""
    nombre = serializers.CharField()
    cantidad_registros = serializers.IntegerField()
    tipos_formulario = serializers.ListField(
        child=serializers.CharField()
    )


class LugaresAgrupadosSerializer(serializers.Serializer):
    """Serializer principal para la respuesta de lugares."""
    lugares_unicos = serializers.ListField(
        child=serializers.CharField()
    )
    lugares_por_tipo = serializers.DictField(
        child=serializers.ListField(
            child=serializers.CharField()
        )
    )
    lugares_con_estadisticas = LugarEstadisticaSerializer(many=True)
    total_lugares_unicos = serializers.IntegerField()
    total_registros = serializers.IntegerField()