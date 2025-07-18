from rest_framework import serializers

class UsuarioResponse(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    usuario = serializers.CharField(required=False, allow_blank=True, max_length=150)
    nombre = serializers.CharField(required=False, allow_blank=True, max_length=150)
    paterno = serializers.CharField(required=False, allow_blank=True, max_length=150)
    materno = serializers.CharField(required=False, allow_blank=True, max_length=150)
    permisos = serializers.CharField(required=False, allow_blank=True, max_length=150)
    activo = serializers.BooleanField(required=False)

class CreateUserResponse(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    mensaje = serializers.CharField(required=False, allow_blank=True, max_length=150)

class AutenticacionUsuarioResponse(serializers.Serializer):
    validacion = serializers.BooleanField(required=False)
    mensaje = serializers.CharField(required=False, allow_blank=True, max_length=150)
    usuario = UsuarioResponse(required=False)
    