# spme/spme_fonfosc/serializers/usuario_fonfosc_serializer.py
from rest_framework import serializers

from spme_fonfosc.models import UsuarioFonFosc


class RegistroUsuarioFonFoscSerializer(serializers.Serializer):
    """Serializer para validar los datos de registro"""

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(min_length=8, write_only=True)
    nombre = serializers.CharField(max_length=30)
    paterno = serializers.CharField(max_length=30)
    materno = serializers.CharField(max_length=150, required=False, allow_blank=True)
    ci = serializers.CharField(max_length=15, required=False, allow_blank=True)
    correo = serializers.EmailField()
    institucion_id = serializers.IntegerField()
    telefono = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate_username(self, value):
        from spme_autenticacion.models import Usuario
        if Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError('El usuario ya existe')
        return value

    def validate_institucion_id(self, value):
        from spme_fonfosc.models import Institucion
        if not Institucion.objects.filter(id=value).exists():
            raise serializers.ValidationError('La institución no existe')
        return value


class UsuarioFonFoscSerializer(serializers.ModelSerializer):
    """Serializer para la respuesta de UsuarioFonFosc"""

    username = serializers.CharField(source='usuario.username', read_only=True)
    nombre = serializers.CharField(source='usuario.nombre', read_only=True)
    paterno = serializers.CharField(source='usuario.paterno', read_only=True)
    materno = serializers.CharField(source='usuario.materno', read_only=True)
    correo = serializers.CharField(source='usuario.correo', read_only=True)
    cargo = serializers.CharField(source='usuario.cargo', read_only=True)
    institucion_nombre = serializers.CharField(source='institucion.nombre', read_only=True)
    institucion_sigla = serializers.CharField(source='institucion.sigla', read_only=True)

    class Meta:
        model = UsuarioFonFosc
        fields = [
            'id',
            'username',
            'nombre',
            'paterno',
            'materno',
            'correo',
            'cargo',
            'institucion',
            'institucion_nombre',
            'institucion_sigla',
            'telefono',
            'creado_en',
        ]