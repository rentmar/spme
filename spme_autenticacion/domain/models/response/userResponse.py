from rest_framework import serializers

class UsuarioResponse(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    usuario = serializers.CharField(required=False, allow_blank=True, max_length=150)
    nombre = serializers.CharField(required=False, allow_blank=True, max_length=150)
    paterno = serializers.CharField(required=False, allow_blank=True, max_length=150)
    materno = serializers.CharField(required=False, allow_blank=True, max_length=150)
    ci = serializers.CharField(required=False,allow_blank=True, max_length=12)
    cargo = serializers.CharField(required=False,allow_blank=True, max_length=50)
    banco = serializers.CharField(required=False,allow_blank=True, max_length=50)
    numeroCuenta = serializers.CharField(required=False,allow_blank=True, max_length=50)
    tipoCuenta = serializers.CharField(required=False,allow_blank=True, max_length=50)
    permisos = serializers.CharField(required=False, allow_blank=True, max_length=20)
    # activo = serializers.BooleanField(required=False)

class CreateUserResponse(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    mensaje = serializers.CharField(required=False, allow_blank=True, max_length=150)

class AutenticacionUsuarioResponse(serializers.Serializer):
    validacion = serializers.BooleanField(required=False)
    mensaje = serializers.CharField(required=False, allow_blank=True, max_length=150)
    usuario = serializers.CharField(required=False, allow_blank=False, max_length=150)
    permisos = serializers.CharField(required=False, allow_blank=True, max_length=20)
    