# spme/spme_repositorio/views/upload_serializers.py
from rest_framework import serializers
from spme_repositorio.models import Archivo, Adjunto


class UploadRequestSerializer(serializers.Serializer):
    archivos = serializers.ListField(
        child=serializers.FileField(),
        required=True,
        min_length=1,
    )
    tipo_objeto = serializers.CharField(required=True)
    objeto_id = serializers.IntegerField(required=True, min_value=1)
    descripcion = serializers.CharField(required=False, allow_blank=True, default='')


class ArchivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Archivo
        fields = [
            'id', 'nombre_original', 'tipo_archivo', 'mime_type',
            'tamano', 'hash_sha256', 'creado_en',
        ]


class AdjuntoSerializer(serializers.ModelSerializer):
    archivo = ArchivoSerializer(read_only=True)

    class Meta:
        model = Adjunto
        fields = ['id', 'archivo', 'descripcion', 'orden', 'creado_en']


class FallidoSerializer(serializers.Serializer):
    nombre_original = serializers.CharField()
    error = serializers.CharField()


class UploadResponseSerializer(serializers.Serializer):
    exitosos = AdjuntoSerializer(many=True)
    fallidos = FallidoSerializer(many=True)
    total = serializers.IntegerField()
    todos_exitosos = serializers.BooleanField()