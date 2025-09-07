from rest_framework import serializers
from spme_estructuracion_proyecto.models import DiagramaEstructura


class DiagramaEstructuraSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagramaEstructura
        fields = [
            'id',
            'codigoProyecto',
            'nodos',
            'conexiones',
            'sincronizado',
            'creado',
            'actualizado',
            'proyecto'
        ]
        read_only_fields = ['id', 'creado', 'actualizado']

