# spme/spme_repositorio/serializers/proyecto_resumen_serializers.py
from rest_framework import serializers


class ConteoArchivosSerializer(serializers.Serializer):
    """Conteo de archivos por tipo."""
    documentos = serializers.IntegerField()
    imagenes = serializers.IntegerField()
    videos = serializers.IntegerField()
    audios = serializers.IntegerField()
    otros = serializers.IntegerField()

class InstanciaGestoraResumenSerializer(serializers.Serializer):
    """Instancia gestora asociada a un proyecto."""
    id = serializers.IntegerField()
    codigo = serializers.CharField(allow_blank=True, allow_null=True)
    clasificador = serializers.CharField(allow_blank=True, allow_null=True)
    instancia = serializers.CharField()


class ProyectoResumenSerializer(serializers.Serializer):
    """Resumen de repositorio de un proyecto."""
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    codigo = serializers.CharField()
    descripcion = serializers.CharField(allow_blank=True, allow_null=True)
    estado = serializers.CharField()
    fecha_creacion = serializers.DateField()
    fecha_actualizacion = serializers.DateField(allow_null=True)
    propietario = serializers.IntegerField(allow_null=True)
    instancias_gestoras = InstanciaGestoraResumenSerializer(many=True)
    totalArchivos = serializers.IntegerField()
    totalReferencias = serializers.IntegerField()
    conteoArchivos = ConteoArchivosSerializer()