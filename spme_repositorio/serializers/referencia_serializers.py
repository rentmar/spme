from rest_framework import serializers
from spme_repositorio.models import ReferenciaExterna


class ReferenciaItemSerializer(serializers.Serializer):
    """Estructura de una referencia dentro del bulk."""
    url = serializers.CharField(max_length=2000)
    nombre = serializers.CharField(max_length=500)
    categoria = serializers.CharField(max_length=50, required=False, default='OTRO')
    descripcion = serializers.CharField(required=False, allow_blank=True, default='')
    orden = serializers.IntegerField(required=False, default=0)


class ReferenciaSerializer(serializers.ModelSerializer):
    """Serializa una ReferenciaExterna para respuestas."""
    class Meta:
        model = ReferenciaExterna
        fields = [
            'id', 'url', 'nombre', 'categoria',
            'descripcion', 'orden', 'creado_en',
        ]


class ReferenciaSingleRequestSerializer(serializers.Serializer):
    """Valida la creación de una referencia."""
    url = serializers.CharField(max_length=2000)
    nombre = serializers.CharField(max_length=500)
    categoria = serializers.CharField(max_length=50, required=False, default='OTRO')
    tipo_objeto = serializers.CharField()
    objeto_id = serializers.IntegerField(min_value=1)
    descripcion = serializers.CharField(required=False, allow_blank=True, default='')
    orden = serializers.IntegerField(required=False, default=0)


class ReferenciaBulkRequestSerializer(serializers.Serializer):
    """Valida la creación de múltiples referencias para un mismo objeto."""
    referencias = serializers.ListField(
        child=ReferenciaItemSerializer(),
        min_length=1,
    )
    tipo_objeto = serializers.CharField()
    objeto_id = serializers.IntegerField(min_value=1)